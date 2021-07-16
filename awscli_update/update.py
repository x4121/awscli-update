'''update AWS CLI if there is a more recent version available'''

from io import BytesIO
import re
import shutil
import subprocess
import tempfile
from zipfile import ZipFile
import requests
from lxml import html

def get_latest_version():
    '''returns the latest available AWS CLI version'''
    changelog_url='https://github.com/aws/aws-cli/blob/v2/CHANGELOG.rst'
    version_xpath='//*[@id="readme"]/article/h2[1]/text()'
    version_regex = re.compile(r'([0-9]+)\.([0-9]+)\.([0-9]+)')
    result = requests.get(changelog_url)
    body = html.fromstring(result.content)
    version = body.xpath(version_xpath)[0]
    match = version_regex.match(version)
    return version if match else None

def get_current_version():
    '''returns the currently installed AWS CLI version'''
    version_regex = re.compile(r'aws-cli\/([0-9.]+)')
    version_string = subprocess.check_output(['aws', '--version']).decode('utf-8')
    match = version_regex.search(version_string)
    return match.groups()[0] if match else None


def install_new_version(version):
    '''Installs new AWS CLI with provided version'''
    tmp = tempfile.mkdtemp()
    url = "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-%s.zip" % version
    result = requests.get(url, allow_redirects=True)
    with ZipFile(BytesIO(result.content)) as zipfile:
        zipfile.extractall(path=tmp)
    install_script = "%s/aws/install" % tmp
    subprocess.call(['chmod', '+x', install_script])
    subprocess.call(['chmod', '-R', '+x', "%s/aws/dist" % tmp])
    subprocess.call(['sudo', install_script, '--update'])
    shutil.rmtree(tmp)

def main():
    '''Check for new version and install if available'''
    current_version = get_current_version()
    latest_version = get_latest_version()
    if not latest_version:
        print("failed to fetch latest version. aborting.")
    if not current_version or current_version != latest_version:
        print("updating awscli from version %s to %s" % (current_version,
            latest_version))
        install_new_version(latest_version)
    else:
        print("awscli already on latest version. skipping.")

if __name__ == "__main__":
    main()
