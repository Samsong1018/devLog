# devlog

A sanitized, running log of my security-tooling, self-hosted-infra, and web
work. Updated as I build; pushed nightly by a systemd timer.

Every push is gated by [`scan-secrets.py`](scan-secrets.py), a fail-closed
pre-push scanner that blocks the push if it detects IP addresses, SSH
`user@host` strings, private keys, cloud credentials, or high-entropy secrets.
The log is written sanitized by hand — the scanner is the backstop.
