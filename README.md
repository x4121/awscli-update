# AWS CLI v2 Update Script

## Usage
```
usage: awscli-update [-h] [--version] [-n]

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
  -n, --noop  only compare versions but don't install
```

### Setup
```bash
python3 -m pip install awscli-update
```

## Development
- Create venv (`python3 -m venv venv`)
- Start venv (`source venv/bin/activate`)
- Install dependencies (`python3 -m pip install setuptools wheel twine versioneer`)
- Install requirements (`python3 -m pip install -r requirements`)
- Build local dist (`python3 setup.py develop --user`)

## Deployment
- Build dist (`python3 setup.py sdist bdist_wheel`)
- Deploy (`twine upload dist/*`)
