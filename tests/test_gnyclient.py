"""Tests for the GNYClient wrapper."""

import unittest
from unittest.mock import MagicMock, patch

from certbot_dns_gny.gnyclient import GNYClient


class TestGNYClient(unittest.TestCase):
    def setUp(self):
        self.client = GNYClient("dns.example.com", "user", "pass")

    def test_base_url(self):
        assert self.client.base_url == "https://dns.example.com/api/"

    def test_auth_is_set(self):
        assert self.client.session.auth == ("user", "pass")

    def test_no_auth_when_omitted(self):
        client = GNYClient("dns.example.com")
        assert client.session.auth is None

    @patch.object(GNYClient, "_request")
    def test_add(self, mock_request):
        self.client.add("_acme.example.com", "token123")
        mock_request.assert_called_once_with(
            "POST",
            "record:txt",
            {"name": "_acme.example.com", "text": "token123"},
        )

    @patch.object(GNYClient, "_request")
    def test_delete(self, mock_request):
        self.client.delete("_acme.example.com", "token123")
        mock_request.assert_called_once_with(
            "DELETE",
            "record:txt",
            {"name": "_acme.example.com", "text": "token123"},
        )

    @patch.object(GNYClient, "_request")
    def test_enroll(self, mock_request):
        self.client.enroll("user@example.com")
        mock_request.assert_called_once_with(
            "POST",
            "enroll",
            {"mail": "user@example.com"},
        )

    @patch.object(GNYClient, "_request")
    def test_test(self, mock_request):
        self.client.test("_acme.example.com")
        mock_request.assert_called_once_with(
            "GET",
            "record:txt/test",
            {"name": "_acme.example.com"},
        )

    @patch("certbot_dns_gny.gnyclient.requests.Session")
    def test_request_calls_session(self, mock_session_cls):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "ok"}
        mock_session.request.return_value = mock_response
        mock_session_cls.return_value = mock_session

        client = GNYClient("dns.example.com", "user", "pass")
        result = client._request("POST", "record:txt", {"name": "test"})

        mock_session.request.assert_called_once_with(
            "POST",
            "https://dns.example.com/api/record:txt",
            json={"name": "test"},
        )
        mock_response.raise_for_status.assert_called_once()
        assert result == {"result": "ok"}


if __name__ == "__main__":
    unittest.main()
