'''update AWS CLI if there is a more recent version available'''

from io import BytesIO
import os
import re
import subprocess
from sys import platform
import tempfile
from zipfile import ZipFile
import argparse
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
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
        help='install aws-cli in custom path (default is /usr/local)')
    return parser.parse_args()

def get_latest_version():
    '''returns the latest available AWS CLI version'''
    changelog_url = 'https://github.com/aws/aws-cli/blob/v2/CHANGELOG.rst'
    version_regex = re.compile(r'([0-9]+)\.([0-9]+)\.([0-9]+)')
    try:
        result = requests.get(changelog_url)
        soup = BeautifulSoup(result.content, 'html.parser')
        readme = soup.find(id='readme')
        version = readme.find_all('h2')[0].text if isinstance(readme, Tag) else ''
        match = version_regex.match(version)
    except (ConnectionError, IndexError) as _:
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
    with tempfile.TemporaryDirectory() as tmp:
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

def _darwin_install(version, args):
    with tempfile.TemporaryDirectory() as tmp:
        pkg = "%s/awscli.pkg" % tmp
        url = "https://awscli.amazonaws.com/AWSCLIV2-%s.pkg" % version.version
        with requests.get(url, allow_redirects=True) as result:
            install_command = ['installer', '-pkg', pkg]
            with open(pkg, 'wb') as file:
                file.write(result.content)
            if args.prefix:
                xml = "%s/choiceChanges.xml" % tmp
                with open(xml, 'w') as file:
                    file.write('''
                    <?xml version="1.0" encoding="UTF-8"?>
                    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
                    <plist version="1.0">
                      <array>
                        <dict>
                          <key>choiceAttribute</key>
                          <string>customLocation</string>
                          <key>attributeSetting</key>
                          <string>%s</string>
                          <key>choiceIdentifier</key>
                          <string>default</string>
                        </dict>
                      </array>
                    </plist>
                    ''' % args.prefix)
                install_command = [
                    *install_command,
                    '-target', 'CurrentUserHomeDirectory',
                    '-applyChoiceChangesXML', xml]
            else:
                install_command = [*install_command, '-target', '/']
            if args.sudo:
                install_command = ['sudo', *install_command]
            if args.quiet:
                subprocess.call(install_command, stdout=subprocess.DEVNULL)
            else:
                subprocess.call(install_command)
            if args.prefix:
                os.makedirs(args.prefix, exist_ok=True)
                aws_bin_src = "%s/aws-cli/aws" % args.prefix
                aws_bin_dst = "%s/bin/aws" % args.prefix
                aws_cmp_src = "%s/aws-cli/aws_completer" % args.prefix
                aws_cmp_dst = "%s/bin/aws_completer" % args.prefix
                if os.path.exists(aws_bin_dst):
                    os.remove(aws_bin_dst)
                if os.path.exists(aws_cmp_dst):
                    os.remove(aws_cmp_dst)
                os.symlink(aws_bin_src, aws_bin_dst)
                os.symlink(aws_cmp_src, aws_cmp_dst)

def _windows_install(version, args):
    if args.sudo or args.prefix:
        print("--sudo and --prefix are not supported on Windows")
        return
    with tempfile.TemporaryDirectory() as tmp:
        msi = "%s/awscliv2.msi" % tmp
        url = "https://awscli.amazonaws.com/AWSCLIV2-%s.msi" % version.version
        with requests.get(url, allow_redirects=True) as result:
            with open(msi, 'wb') as file:
                file.write(result.content)
            install_command = ['msiexec.exe', '/i', msi, '/passive']
            if args.quiet:
                subprocess.call(install_command, stdout=subprocess.DEVNULL)
            else:
                subprocess.call(install_command)

def install_new_version(version, args):
    '''Installs new AWS CLI with provided version'''
    if not version.v_2:
        print("This script can only install AWS CLI v2")
        return
    if platform == 'linux':
        _linux_install(version, args)
    elif platform == 'darwin':
        _darwin_install(version, args)
    elif platform == 'win32':
        _windows_install(version, args)
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
