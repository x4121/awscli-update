# AWS CLI v2 Update Script

## Usage
`awscli-update`

### Setup
```bash
python3 -m pip install awscli-update
```
## Deployment
- Install dependencies (`python3 -m pip install setuptools wheel twine`)
- (optional) build local dist (`pyton3 setup.py develop --user`)
- Build dist (`python3 setup.py sdist bdist_wheel`)
- Deploy (`twine upload --repository-url https://ryte.jfrog.io/ryte/api/pypi/pypi-local/ dist/*`)
