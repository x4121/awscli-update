# pylint: disable=missing-module-docstring

from setuptools import setup, find_packages
import versioneer


with open('README.md') as f:
    readme = f.read()

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
    license='MIT',
    packages=find_packages(exclude=('tests', 'docs')),
    scripts=['bin/awscli-update'],
    install_requires=required,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Installation/Setup',
        'Topic :: Utilities'
    ]
)
