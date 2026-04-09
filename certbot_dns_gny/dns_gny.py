"""DNS Authenticator for GNY."""

from collections.abc import Callable

from certbot.plugins import dns_common

from .gnyclient import GNYClient


class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for GNY

    This Authenticator uses the GNY API to fulfill a
    dns-01 challenge."""

    description = "Obtain certificates using a DNS TXT record (if you are using GNY)."

    _gnyclient = None

    @classmethod
    def add_parser_arguments(
        cls, add: Callable[..., None], default_propagation_seconds: int = 120
    ) -> None:
        super().add_parser_arguments(add, default_propagation_seconds)
        add(
            "credentials",
            help="GNY credentials INI file.",
            default="/etc/letsencrypt/gny.ini",
        )

    def more_info(self):
        return (
            "This plugin configures a DNS TXT record to respond to a "
            "dns-01 challenge using the GNY API."
        )

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            "credentials",
            "GNY credentials INI file",
            {
                "hostname": "Hostname for GNY server",
                "username": "Username for GNY API.",
                "password": "Password for GNY API.",
            },
        )

    def _setup_gnyclient(self):
        if not self._gnyclient:
            self._setup_credentials()
            self._gnyclient = GNYClient(
                self.credentials.conf("hostname"),
                self.credentials.conf("username"),
                self.credentials.conf("password"),
            )

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        self._setup_gnyclient()
        self._gnyclient.add(validation_name, validation)

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        self._setup_gnyclient()
        self._gnyclient.delete(validation_name, validation)
