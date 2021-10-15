# AWS CLI v2 Update Script
[![PyPI - awscli-update](https://img.shields.io/pypi/v/awscli-update.svg?color=blue&label=awscli-update)](https://pypi.org/project/awscli-update)

A small script to keep the AWS CLI v2 up to date,
[until AWS figures out how to distribute software
properly](https://github.com/aws/aws-cli/issues/4947).

## Usage
```
usage: awscli-update [-h] [--version] [-n] [-q] [--no-sudo] [--prefix PREFIX]

optional arguments:
  -h, --help       show this help message and exit
  --version        show program's version number and exit
  -n, --noop       only compare versions but don't install
  -q, --quiet      only print error messages when updating
  --sudo           use sudo to install (e.g. when installing to /usr/local)
  --prefix PREFIX  install aws-cli in custom path (default is /usr/local)
```

### Setup
```bash
python3 -m pip install awscli-update
```

### Auto update
#### Linux
Assuming the `awscli-update` binary is installed in `$HOME/.local/bin`
(check the location on your machine by running `which awscli-update`),
you want to install the AWS CLI in `$HOME/.local/bin` and
you want to check for updates every hour,
run `crontab -e` and add following line
```
0 * * * * $HOME/.local/bin/awscli-update -q --prefix $HOME/.local
```

#### macOS
Assuming the `awscli-update` binary is installed in `/opt/homebrew/bin`
(check the location on your machine by running `which awscli-update`),
you want to install the AWS CLI in `/opt/homebrew/bin` and
you want to check for updates every hour,
run `crontab -e` and add following line
```
PATH=$PATH:/usr/sbin
0 * * * * /opt/homebrew/bin/awscli-update -q --prefix /opt/homebrew
```

#### General things
If you want to check for updates more/less often or at specific times,
check [this editor for cron expressions](https://crontab.guru/).

## Development
- Create venv (`python3 -m venv venv`)
- Start venv (`source venv/bin/activate`)
- Install dependencies (`python3 -m pip install setuptools wheel twine versioneer`)
- Install requirements (`python3 -m pip install -r requirements.txt`)
- Build local dist (`python3 setup.py develop --user`)

## Deployment
- Build dist (`python3 setup.py sdist bdist_wheel`)
- Deploy (`twine upload dist/*`)
