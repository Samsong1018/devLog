#!/usr/bin/env python3
"""Pre-push secret/PII scanner for the public devlog.

Fails CLOSED: any finding exits non-zero so the push is blocked. Tuned for a
prose work-log plus Amos's specific infrastructure. A false positive just
pauses the push for a human look — the safe direction to be wrong in.

Usage: scan-secrets.py FILE [FILE ...]
"""
import ipaddress
import re
import sys

# ── High-confidence patterns (any match blocks the push) ─────────────────────
PATTERNS = [
    ("private-key", re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")),
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("ssh-user-at-host", re.compile(r"\b[a-z_][a-z0-9_-]*@"
                                    r"(?:\d{1,3}(?:\.\d{1,3}){3}"
                                    r"|[a-z0-9-]+(?:\.[a-z0-9-]+)*)", re.I)),
    ("secret-assignment", re.compile(
        r"(?i)\b(?:pass(?:word|wd)?|secret|token|api[_-]?key|bearer|"
        r"client[_-]?secret|private[_-]?key)\b\s*[:=]\s*\S{6,}")),
    ("env-token", re.compile(
        r"\b(?:DASHBOARD_TOKEN|SHIPPER_TOKEN|BATTERY_TOKEN|ADGUARD_PASS)"
        r"\s*=\s*\S+")),
    # Long high-entropy runs — real hashes, keys, tokens (not 7-char git shas).
    ("hex-blob", re.compile(r"\b[0-9a-fA-F]{32,}\b")),
    ("base64-blob", re.compile(r"\b[A-Za-z0-9+/]{40,}={0,2}\b")),
]

# Candidate IPv4/IPv6, validated below to cut semver false positives.
IPV4 = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
IPV6 = re.compile(r"\b(?:[0-9A-Fa-f]{1,4}:){2,7}[0-9A-Fa-f]{1,4}\b")

# Documentation/loopback ranges that are safe to publish (never real infra).
SAFE_IPS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("0.0.0.0/32"),
    ipaddress.ip_network("255.255.255.255/32"),
    ipaddress.ip_network("192.0.2.0/24"),    # TEST-NET-1 (docs)
    ipaddress.ip_network("198.51.100.0/24"), # TEST-NET-2 (docs)
    ipaddress.ip_network("203.0.113.0/24"),  # TEST-NET-3 (docs)
]


def mask(s: str) -> str:
    s = s.strip()
    return s if len(s) <= 8 else f"{s[:4]}…{s[-2:]}"


def scan_line(line: str):
    hits = []
    for name, pat in PATTERNS:
        for m in pat.finditer(line):
            hits.append((name, m.group(0)))
    for m in IPV4.finditer(line):
        try:
            ip = ipaddress.ip_address(m.group(0))
        except ValueError:
            continue  # not a real IP (e.g. a 4-part version like 1.2.3.4→>255)
        if any(ip in net for net in SAFE_IPS):
            continue
        hits.append(("ipv4", m.group(0)))
    for m in IPV6.finditer(line):
        try:
            ipaddress.ip_address(m.group(0))
        except ValueError:
            continue
        hits.append(("ipv6", m.group(0)))
    return hits


def main(paths):
    findings = []
    for path in paths:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                for n, line in enumerate(f, 1):
                    for name, match in scan_line(line):
                        findings.append((path, n, name, match))
        except FileNotFoundError:
            continue
    if findings:
        print("PUSH BLOCKED — possible sensitive data in the devlog:\n",
              file=sys.stderr)
        for path, n, name, match in findings:
            print(f"  {path}:{n}  [{name}]  {mask(match)}", file=sys.stderr)
        print(f"\n{len(findings)} finding(s). Fix or redact, then retry.",
              file=sys.stderr)
        return 1
    print("scan clean — no secrets or IPs detected")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: scan-secrets.py FILE [FILE ...]", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
