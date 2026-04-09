"""Tests for the Authenticator plugin."""

import unittest
from unittest.mock import MagicMock, patch

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

    def test_more_info(self):
        assert "dns-01" in self.auth.more_info()
        assert "GNY" in self.auth.more_info()

    def test_add_parser_arguments(self):
        mock_add = MagicMock()
        Authenticator.add_parser_arguments(mock_add)
        mock_add.assert_any_call(
            "credentials",
            help="GNY credentials INI file.",
            default="/etc/letsencrypt/gny.ini",
        )

    @patch("certbot_dns_gny.dns_gny.GNYClient")
    def test_setup_gnyclient_creates_client(self, mock_client_cls):
        auth = Authenticator(config=MagicMock(), name="dns-gny")
        mock_creds = MagicMock()
        mock_creds.conf.side_effect = lambda k: {
            "hostname": "dns.example.com",
            "username": "user",
            "password": "pass",
        }[k]
        auth.credentials = mock_creds
        auth._setup_credentials = MagicMock()

        auth._setup_gnyclient()

        mock_client_cls.assert_called_once_with("dns.example.com", "user", "pass")
        assert auth._gnyclient == mock_client_cls.return_value

    @patch("certbot_dns_gny.dns_gny.GNYClient")
    def test_setup_gnyclient_reuses_existing(self, mock_client_cls):
        auth = Authenticator(config=MagicMock(), name="dns-gny")
        auth._gnyclient = MagicMock()
        auth._setup_gnyclient()
        mock_client_cls.assert_not_called()


if __name__ == "__main__":
    unittest.main()
