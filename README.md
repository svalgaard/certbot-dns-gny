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
dns_gny_token = your-bearer-token
```

Protect the file:

```bash
chmod 600 /etc/letsencrypt/gny.ini
```

You can also generate a credentials file automatically using `gnyclient enroll` (see below).

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

## gnyclient

The package includes a `gnyclient` command-line tool for enrollment and testing.

### Enroll

Register with a GNY server and generate a credentials file:

```bash
gnyclient enroll gny.example.com you@example.com
```

This enrolls the server as a GNY client with your email address as contact, and writes the returned credentials to `/etc/letsencrypt/gny.ini` (with mode `0600`). You must confirm the enrollment by subsequently accessing the GNY server directly.
Use `-c` to specify a different path:

```bash
gnyclient -c /path/to/gny.ini enroll dns.example.com you@example.com
```

### Test

Verify that the ACME challenge DNS record for a domain is obtainable:

```bash
gnyclient test example.com
```

This performs a test lookup for `_acme-challenge.example.com` via the GNY API using the credentials file.

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
