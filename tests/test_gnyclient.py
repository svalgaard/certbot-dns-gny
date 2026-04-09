"""Tests for the GNYClient wrapper."""

import argparse
import os
import unittest
from unittest.mock import MagicMock, mock_open, patch

from certbot_dns_gny.gnyclient import (
    GNYClient,
    _cmd_enroll,
    _cmd_test,
    _load_credentials,
    main,
)


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


class TestLoadCredentials(unittest.TestCase):
    def test_load_credentials(self):
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            f.write("[DEFAULT]\n")
            f.write("dns_gny_hostname = dns.example.com\n")
            f.write("dns_gny_username = myuser\n")
            f.write("dns_gny_password = mypass\n")
            path = f.name

        try:
            client = _load_credentials(path)
            assert client.host == "dns.example.com"
            assert client.session.auth == ("myuser", "mypass")
        finally:
            os.unlink(path)


class TestCmdEnroll(unittest.TestCase):
    @patch("certbot_dns_gny.gnyclient.os.chmod")
    @patch("certbot_dns_gny.gnyclient.os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch.object(GNYClient, "enroll")
    def test_enroll_writes_credentials(
        self, mock_enroll, mock_file, mock_makedirs, mock_chmod
    ):
        mock_enroll.return_value = {"username": "u1", "password": "p1"}
        args = argparse.Namespace(
            hostname="dns.example.com",
            mail="user@example.com",
            credentials="/tmp/test-gny.ini",
        )

        _cmd_enroll(args)

        mock_enroll.assert_called_once_with("user@example.com")
        mock_makedirs.assert_called_once_with("/tmp", exist_ok=True)
        mock_file.assert_called_once_with("/tmp/test-gny.ini", "w")
        mock_chmod.assert_called_once_with("/tmp/test-gny.ini", 0o600)

    @patch("certbot_dns_gny.gnyclient.os.chmod")
    @patch("certbot_dns_gny.gnyclient.os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch.object(GNYClient, "enroll")
    def test_enroll_saves_hostname_in_config(
        self, mock_enroll, mock_file, mock_makedirs, mock_chmod
    ):
        mock_enroll.return_value = {"username": "u1", "password": "p1"}
        args = argparse.Namespace(
            hostname="gny.example.com",
            mail="a@b.com",
            credentials="/tmp/gny.ini",
        )

        _cmd_enroll(args)

        written = "".join(call.args[0] for call in mock_file().write.call_args_list)
        assert "dns_gny_hostname = gny.example.com" in written
        assert "dns_gny_username = u1" in written
        assert "dns_gny_password = p1" in written


class TestCmdTest(unittest.TestCase):
    @patch("certbot_dns_gny.gnyclient._load_credentials")
    def test_calls_test_with_acme_prefix(self, mock_load):
        mock_client = MagicMock()
        mock_client.test.return_value = {"status": "ok"}
        mock_load.return_value = mock_client

        args = argparse.Namespace(
            credentials="/etc/letsencrypt/gny.ini",
            domain="example.com",
        )

        _cmd_test(args)

        mock_load.assert_called_once_with("/etc/letsencrypt/gny.ini")
        mock_client.test.assert_called_once_with("_acme-challenge.example.com")


class TestMain(unittest.TestCase):
    @patch("certbot_dns_gny.gnyclient._cmd_enroll")
    def test_main_enroll(self, mock_cmd):
        with patch("sys.argv", ["gnyclient", "enroll", "dns.example.com", "a@b.com"]):
            main()
        args = mock_cmd.call_args[0][0]
        assert args.command == "enroll"
        assert args.hostname == "dns.example.com"
        assert args.mail == "a@b.com"

    @patch("certbot_dns_gny.gnyclient._cmd_test")
    def test_main_test(self, mock_cmd):
        with patch("sys.argv", ["gnyclient", "test", "example.com"]):
            main()
        args = mock_cmd.call_args[0][0]
        assert args.command == "test"
        assert args.domain == "example.com"

    @patch("certbot_dns_gny.gnyclient._cmd_test")
    def test_main_custom_credentials(self, mock_cmd):
        with patch(
            "sys.argv", ["gnyclient", "-c", "/tmp/custom.ini", "test", "example.com"]
        ):
            main()
        args = mock_cmd.call_args[0][0]
        assert args.credentials == "/tmp/custom.ini"

    def test_main_no_command_exits(self):
        with patch("sys.argv", ["gnyclient"]):
            with self.assertRaises(SystemExit):
                main()


if __name__ == "__main__":
    unittest.main()
