"""Tests for the Authenticator plugin."""

import unittest
from unittest.mock import MagicMock

from certbot_dns_gny.dns_gny import Authenticator


class TestAuthenticator(unittest.TestCase):
    def setUp(self):
        self.auth = Authenticator(config=MagicMock(), name="dns-gny")
        self.mock_client = MagicMock()
        self.auth._gnyclient = self.mock_client
        # Bypass credential file loading since we already have a client
        self.auth._setup_credentials = MagicMock()

    def test_perform_calls_add(self):
        self.auth._perform("example.com", "_acme.example.com", "token123")
        self.mock_client.add.assert_called_once_with("_acme.example.com", "token123")

    def test_cleanup_calls_delete(self):
        self.auth._cleanup("example.com", "_acme.example.com", "token123")
        self.mock_client.delete.assert_called_once_with("_acme.example.com", "token123")


if __name__ == "__main__":
    unittest.main()
