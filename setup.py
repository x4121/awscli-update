from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='awscli-update',
    version='0.1.0',
    description='CLI tool to update AWS CLI 2',
    long_description=readme,
    author='Armin Grodon',
    author_email='me@armingrodon.de',
    url='https://github.com/x4121/awscli-update',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    scripts=['bin/awscli-update'],
    install_requires=required
)
