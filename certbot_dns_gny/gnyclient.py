#
# GNY Client module - a thin wrapper around the GNY API
#

from __future__ import annotations

import argparse
import configparser
import os

import requests

DEFAULT_CREDENTIALS = "/etc/letsencrypt/gny.ini"
DEFAULT_TIMEOUT = 30
PREFIX = "dns_gny_"


class GNYClient:
    """Thin wrapper around a requests.Session configured for the GNY API."""

    def __init__(self, hostname: str, token: str | None = None):
        self.host = hostname
        self.base_url = f"https://{self.host}/api/"
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _request(
        self,
        method: str,
        url: str,
        payload: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        response = self.session.request(
            method,
            f"{self.base_url}{url}",
            json=payload,
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    def enroll(self, mail: str):
        payload = {"mail": mail}
        return self._request("POST", "enroll", payload)

    def add(self, validation_name: str, validation: str):
        payload = {"name": validation_name, "text": validation}
        return self._request("POST", "txt", payload)

    def delete(self, validation_name: str, validation: str):
        payload = {"name": validation_name, "text": validation}
        return self._request("DELETE", "txt", payload)

    def test(self, validation_name: str):
        return self._request("GET", "txt/test", params={"name": validation_name})


def _load_credentials(path: str) -> GNYClient:
    """Read a certbot-style INI credentials file and return a configured GNYClient."""
    cfg = configparser.ConfigParser()
    cfg.read(path)
    section = cfg.defaults()
    return GNYClient(
        section[f"{PREFIX}hostname"],
        section[f"{PREFIX}token"],
    )


def _cmd_enroll(args: argparse.Namespace) -> None:
    client = GNYClient(args.hostname)
    result = client.enroll(args.mail)

    cfg = configparser.ConfigParser()
    cfg.set(configparser.DEFAULTSECT, f"{PREFIX}hostname", args.hostname)
    for key, value in result.items():
        cfg.set(configparser.DEFAULTSECT, f"{PREFIX}{key}", str(value))

    path = args.credentials
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        cfg.write(f)
    os.chmod(path, 0o600)
    print(f"Credentials written to {path}")


def _cmd_test(args: argparse.Namespace) -> None:
    client = _load_credentials(args.credentials)
    fqdn = f"_acme-challenge.{args.domain}"
    result = client.test(fqdn)
    print(result)


def main():
    parser = argparse.ArgumentParser(description="GNY DNS API client")
    parser.add_argument(
        "-c",
        "--credentials",
        default=DEFAULT_CREDENTIALS,
        help=f"Path to credentials INI file (default: {DEFAULT_CREDENTIALS})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    enroll_parser = sub.add_parser("enroll", help="Enroll with a GNY server")
    enroll_parser.add_argument("hostname", help="GNY server hostname")
    enroll_parser.add_argument("mail", help="Email address for enrollment")

    test_parser = sub.add_parser("test", help="Test ACME challenge DNS lookup")
    test_parser.add_argument("domain", help="Domain name to test")

    args = parser.parse_args()
    if args.command == "enroll":
        _cmd_enroll(args)
    elif args.command == "test":
        _cmd_test(args)


if __name__ == "__main__":
    main()
