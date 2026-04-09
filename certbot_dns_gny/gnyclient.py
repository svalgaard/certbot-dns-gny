#
# GNY Client module - a thin wrapper around the GNY API
#

import requests


class GNYClient:
    """Thin wrapper around a requests.Session configured for the GNY API."""

    def __init__(self, hostname: str, username: str = None, password: str = None):
        self.host = hostname
        self.base_url = f"https://{self.host}/api/"
        self.session = requests.Session()
        if username and password:
            self.session.auth = (username, password)

    def _request(self, method: str, url: str, payload: dict = {}) -> dict:
        response = self.session.request(method, f"{self.base_url}{url}", json=payload)
        response.raise_for_status()
        return response.json()

    def enroll(self, mail: str):
        payload = {"mail": mail}
        return self._request("POST", "enroll", payload)

    def add(self, validation_name: str, validation: str):
        payload = {"name": validation_name, "text": validation}
        return self._request("POST", "record:txt", payload)

    def delete(self, validation_name: str, validation: str):
        payload = {"name": validation_name, "text": validation}
        return self._request("DELETE", "record:txt", payload)

    def test(self, validation_name: str):
        payload = {"name": validation_name}
        return self._request("GET", "record:txt/test", payload)
