# AWS CLI v2 Update Script

## Usage
`awscli-update`

### Setup
```bash
python3 -m pip install awscli-update
```

## Development
- Create venv (`python3 -m venv .venv`)
- Install requirements (`python3 -m pip install -r requirements`)
- Build local dist (`python3 setup.py develop --user`)

## Deployment
- Install dependencies (`python3 -m pip install setuptools wheel twine`)
- Build dist (`python3 setup.py sdist bdist_wheel`)
- Deploy (`twine upload dist/*`)
