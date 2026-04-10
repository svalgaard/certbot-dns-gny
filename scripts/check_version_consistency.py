#!/usr/bin/env python3
"""Check that version numbers are consistent across project files."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def get_pyproject_version():
    text = (ROOT / "pyproject.toml").read_text()
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not m:
        sys.exit("ERROR: could not find version in pyproject.toml")
    return m.group(1)


def get_init_version():
    text = (ROOT / "certbot_dns_gny" / "__init__.py").read_text()
    m = re.search(r'^__version__\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not m:
        sys.exit("ERROR: could not find __version__ in certbot_dns_gny/__init__.py")
    return m.group(1)


def get_changelog_version():
    text = (ROOT / "debian" / "changelog").read_text()
    # First line: "certbot-dns-gny (UPSTREAM-DEBREV) ..."
    m = re.match(r"^\S+\s+\(([^)]+)\)", text)
    if not m:
        sys.exit("ERROR: could not parse version from debian/changelog")
    full = m.group(1)
    # Strip the Debian revision (everything after the last hyphen)
    upstream = full.rsplit("-", 1)[0]
    return upstream, full


def main():
    pyproject = get_pyproject_version()
    init = get_init_version()
    changelog_upstream, changelog_full = get_changelog_version()

    ok = True
    if pyproject != init:
        print(
            f"MISMATCH: pyproject.toml has {pyproject!r} but __init__.py has {init!r}"
        )
        ok = False
    if pyproject != changelog_upstream:
        print(
            f"MISMATCH: pyproject.toml has {pyproject!r} "
            f"but debian/changelog has {changelog_full!r} "
            f"(upstream part: {changelog_upstream!r})"
        )
        ok = False

    if ok:
        print(f"OK: all versions consistent ({pyproject})")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
