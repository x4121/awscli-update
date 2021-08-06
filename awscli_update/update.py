'''update AWS CLI if there is a more recent version available'''

from io import BytesIO
import os
import re
import shutil
import subprocess
from sys import platform
import tempfile
from zipfile import ZipFile
import argparse
import requests
from lxml import html, etree
from . import __version__

class Version:
    '''AWS CLI version'''
    def __init__(self, version, v_2=True):
        self.version = version
        self.v_2 = v_2

    def to_string(self):
        '''Create printable string from version info'''
        if self.v_2:
            return self.version
        return '%s (AWS CLI v1!)' % self.version

    def __eq__(self, other):
        if isinstance(other, Version):
            return self.version == other.version and self.v_2 == other.v_2
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


def _parse_arguments():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument(
        '-n',
        '--noop',
        action='store_true',
        help='''only compare versions but don't install''')
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='only print error messages when updating')
    parser.add_argument(
        '--sudo',
        dest='sudo',
        action='store_true',
        help='''use sudo to install (e.g. when installing to /usr/local)''')
    parser.add_argument(
        '--prefix',
        help=(
            'install aws-cli in custom path (default is /usr/local)\n' +
            'only working on Linux right now'))
    return parser.parse_args()

def get_latest_version():
    '''returns the latest available AWS CLI version'''
    changelog_url = 'https://github.com/aws/aws-cli/blob/v2/CHANGELOG.rst'
    version_xpath = '//*[@id="readme"]/article/h2[1]/text()'
    version_regex = re.compile(r'([0-9]+)\.([0-9]+)\.([0-9]+)')
    try:
        result = requests.get(changelog_url)
        body = html.fromstring(result.content)
        version = body.xpath(version_xpath)[0]
        match = version_regex.match(version)
    except (ConnectionError, IndexError, etree.ParserError) as _:
        return None
    return Version(version) if match else None

def get_current_version():
    '''returns the currently installed AWS CLI version'''
    version_regex = re.compile(r'aws-cli\/([0-9.]+)')
    version_v2_regex = re.compile(r'2\.([0-9]+)\.([0-9]+)')
    try:
        version_string = subprocess.check_output(['aws', '--version']).decode('utf-8')
        match = version_regex.search(version_string)
        version = match.groups()[0] if match else None
        v_2 = version is not None and version_v2_regex.match(version) is not None
    except (FileNotFoundError, IndexError) as _:
        return None
    return Version(version, v_2)

def _linux_install(version, args):
    tmp = tempfile.mkdtemp()
    url = "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-%s.zip" % version.version
    with requests.get(url, allow_redirects=True) as result:
        with ZipFile(BytesIO(result.content)) as zipfile:
            zipfile.extractall(path=tmp)
        install_script = "%s/aws/install" % tmp
        install_command = [install_script, '--update']
        if args.prefix:
            install_command = [
                *install_command,
                '--install-dir', "%s/aws-cli" % args.prefix,
                '--bin-dir', "%s/bin" % args.prefix
            ]
        if args.sudo:
            install_command = ['sudo', *install_command]
        os.chmod(install_script, 0o755)
        for root, _, files in os.walk("%s/aws/dist" % tmp):
            for file in files:
                os.chmod(os.path.join(root, file), 0o755)
        if args.quiet:
            subprocess.call(install_command, stdout=subprocess.DEVNULL)
        else:
            subprocess.call(install_command)
    shutil.rmtree(tmp)

def _darwin_install(version, args):
    if args.prefix:
        print("argument `--prefix` doesn't work on Mac OS (right now). aborting.")
        return
    tmp = tempfile.mkdtemp()
    url = "https://awscli.amazonaws.com/AWSCLIV2-%s.pkg" % version.version
    with requests.get(url, allow_redirects=True) as result:
        pkg_file = "%s/aws/install" % tmp
        install_command = ['installer', '--pkg', pkg_file, '-target', '/']
        with open(pkg_file, 'wb') as file:
            shutil.copyfileobj(result.raw, file)
        if args.sudo:
            install_command = ['sudo', *install_command]
        if args.quiet:
            subprocess.call(install_command, stdout=subprocess.DEVNULL)
        else:
            subprocess.call(install_command)
    shutil.rmtree(tmp)

def install_new_version(version, args):
    '''Installs new AWS CLI with provided version'''
    if not version.v_2:
        print("This script can only install AWS CLI v2")
        return
    if platform == 'linux':
        _linux_install(version, args)
    elif platform == 'darwin':
        _darwin_install(version, args)
    else:
        pass

def compare_only():
    '''Check for new version but don't update'''
    current_version = get_current_version()
    latest_version = get_latest_version()
    if not latest_version:
        print("failed to fetch latest version. aborting.")
    else:
        print("current version: %s" % (current_version.to_string() if
            current_version else None))
        print("latest  version: %s" % (latest_version.to_string() if
            latest_version else None))

def compare_and_update(args):
    '''Check for new version and install if available'''
    current_version = get_current_version()
    latest_version = get_latest_version()
    if not latest_version:
        print("failed to fetch latest version. aborting.")
    elif current_version and not current_version.v_2:
        print("AWS CLI v1 installed. Remove AWS CLI v1 first. aborting")
    elif not current_version:
        if not args.quiet:
            print("installing AWS CLI version %s" % latest_version.version)
        install_new_version(latest_version, args)
    elif current_version != latest_version:
        if not args.quiet:
            print("updating AWS CLI from version %s to %s" %
              (current_version.version, latest_version.version))
        install_new_version(latest_version, args)
    else:
        if not args.quiet:
            print("AWS CLI already on latest version. skipping.")

def main():
    '''Module main loop'''
    args = _parse_arguments()
    if args.noop:
        compare_only()
    else:
        compare_and_update(args)
