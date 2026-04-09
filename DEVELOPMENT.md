# Development Guide

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[test,lint]"
```

## Testing

```bash
pytest -v
```

## Linting

```bash
ruff check .
ruff format --check .
```

## Building a Debian Package

```bash
sudo apt-get install debhelper dh-python pybuild-plugin-pyproject \
    python3-all python3-setuptools python3-certbot python3-requests
dpkg-buildpackage -us -uc -b
```

## Release Process

1. Bump version in `pyproject.toml` and `certbot_dns_gny/__init__.py`
2. Update `debian/changelog`
3. Commit and push to `main`
4. Tag and push:
   ```bash
   git tag v0.x.0
   git push origin v0.x.0
   ```
   The `release.yml` workflow will automatically create a GitHub Release
   with notes extracted from `debian/changelog` and attach the `.deb`.
