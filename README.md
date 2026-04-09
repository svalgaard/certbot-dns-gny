# certbot-dns-gny

Certbot DNS Authenticator plugin for GNY.

This plugin automates the process of completing a `dns-01` challenge by creating and cleaning up TXT records using the GNY API.

## Installation

```bash
pip install certbot-dns-gny
```

## Credentials

Create an INI file (e.g. `/etc/letsencrypt/gny.ini`) with your GNY API credentials:

```ini
dns_gny_hostname = dns.example.com
dns_gny_username = myuser
dns_gny_password = mysecretpassword
```

Protect the file:

```bash
chmod 600 /etc/letsencrypt/gny.ini
```

## Usage

```bash
certbot certonly \
  --authenticator dns-gny \
  --dns-gny-credentials /etc/letsencrypt/gny.ini \
  -d example.com
```

### Options

| Option | Description | Default |
|---|---|---|
| `--dns-gny-credentials` | Path to credentials INI file | `/etc/letsencrypt/gny.ini` |
| `--dns-gny-propagation-seconds` | Seconds to wait for DNS propagation | `120` |

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
