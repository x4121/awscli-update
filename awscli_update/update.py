# pylint: disable=too-few-public-methods

'''update AWS CLI if there is a more recent version available'''

from io import BytesIO
import re
import shutil
import subprocess
from sys import platform
import tempfile
from zipfile import ZipFile
import argparse
import requests
from lxml import html, etree
import versioneer

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


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=versioneer.get_version()))
    parser.add_argument(
        '-n',
        '--noop',
        action='store_true',
        help='''only compare versions but don't install''')
    return parser.parse_args()

def get_latest_version():
    '''returns the latest available AWS CLI version'''
    changelog_url = 'https://github.com/aws/aws-cli/blob/v2/CHANGELOG.rst'
    version_xpath = '//*[@id="readme"]/article/h2[1]/text()'
    version_regex = re.compile(r'([0-9]+)\.([0-9]+)\.([0-9]+)')
    result = requests.get(changelog_url)
    try:
        body = html.fromstring(result.content)
        version = body.xpath(version_xpath)[0]
        match = version_regex.match(version)
    except (IndexError, etree.ParserError) as _:
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
        v_2 = version_v2_regex.match(version) if version else False
    except (FileNotFoundError, IndexError) as _:
        return None
    return Version(version, v_2)


def install_new_version(version):
    '''Installs new AWS CLI with provided version'''
    if not version.v_2:
        print("This script can only install AWS CLI v2")
        return
    if platform == 'linux':
        tmp = tempfile.mkdtemp()
        url = "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-%s.zip" % version.version
        with requests.get(url, allow_redirects=True) as result:
            with ZipFile(BytesIO(result.content)) as zipfile:
                zipfile.extractall(path=tmp)
            install_script = "%s/aws/install" % tmp
            subprocess.call(['chmod', '+x', install_script])
            subprocess.call(['chmod', '-R', '+x', "%s/aws/dist" % tmp])
            subprocess.call(['sudo', install_script, '--update'])
        shutil.rmtree(tmp)
    elif platform == 'darwin':
        tmp = tempfile.mkdtemp()
        url = "https://awscli.amazonaws.com/AWSCLIV2-%s.pkg" % version.version
        with requests.get(url, allow_redirects=True) as result:
            pkg_file = "%s/aws/install" % tmp
            with open(pkg_file, 'wb') as file:
                shutil.copyfileobj(result.raw, file)
            subprocess.call(['sudo', 'installer', '--pkg', pkg_file, '-target', '/'])
        shutil.rmtree(tmp)
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

def compare_and_update():
    '''Check for new version and install if available'''
    current_version = get_current_version()
    latest_version = get_latest_version()
    if not latest_version:
        print("failed to fetch latest version. aborting.")
    elif current_version and not current_version.v_2:
        print("AWS CLI v1 installed. Remove AWS CLI v1 first. aborting")
    elif not current_version:
        print("installing AWS CLI version %s" % latest_version.version)
        install_new_version(latest_version)
    elif current_version != latest_version:
        print("updating AWS CLI from version %s to %s" %
              (current_version.version, latest_version.version))
        install_new_version(latest_version)
    else:
        print("awscli already on latest version. skipping.")

def main():
    '''Module main loop'''
    args = _parse_arguments()
    if args.noop:
        compare_only()
    else:
        compare_and_update()
