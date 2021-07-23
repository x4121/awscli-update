# pylint: disable=missing-module-docstring
# pylint: disable=redefined-builtin

from setuptools import setup, find_packages
import versioneer


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='awscli-update',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='CLI tool to update AWS CLI 2',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Armin Grodon',
    author_email='me@armingrodon.de',
    url='https://github.com/x4121/awscli-update',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    scripts=['bin/awscli-update'],
    install_requires=required
)
