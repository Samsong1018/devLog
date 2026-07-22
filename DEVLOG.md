# Devlog

A running log of what I'm building — security tooling, self-hosted infra, and
web projects. Sanitized on purpose: no addresses, hostnames, or secrets. The
interesting part is the work, not the IPs.

---

## 2026-07-19

- Added TOTP two-factor auth to my self-hosted VPN dashboard (FastAPI + pyotp).
  Login now needs the access token plus a 6-digit code; a successful login
  mints a short-lived server-side session, so a leaked token alone is useless.
  Added replay protection, constant-time token comparison, and a fail2ban jail
  on the login endpoint.
- Hardened logging on the VPN box against tampering — append-only file
  attributes plus real-time forwarding to a separate append-only sink, so logs
  can't be quietly scrubbed even with root.
- Added a second, append-only backup destination for the VPN configs, with a
  scanner that refuses to overwrite existing backups.
- Shipped DRILL, a terminal-style cybersecurity reflex trainer (exact port
  numbers, HTTP status codes, subnet/CIDR math, Linux CLI) with adaptive
  difficulty and Leitner spaced repetition.
- Triaged a rootkit-scanner alert (turned out benign — unattended security
  upgrades shifting file hashes) and documented the recurring pattern.
- Stood up a temporary Reticulum mesh node to explore the network.
- Built a fail-closed secret-scanning pipeline for this devlog: a pre-push git
  hook and scanner that block any commit containing IP addresses, credentials,
  keys, or high-entropy secrets, feeding a nightly automated publish. Verified
  it aborts a real push the moment a leak is present.

## 2026-07-20

- Replaced the soft, instruction-based reminder that kept this devlog updated
  with real enforcement: a pair of hooks in my Claude Code config, one firing
  at session end and one firing right before long conversations get
  compacted (the exact moment a "remember to do X" instruction tends to get
  lost). Detection reads the session's own file-edit history directly instead
  of depending on git commits, since a lot of my projects don't push anymore —
  so it works the same regardless of whether a project uses git at all. If
  real work happened without this log getting updated, the session-end hook
  blocks the session from closing until it's addressed; the pre-compaction
  hook injects a reminder before the detail gets lost to summarization.
- Ran a full functionality audit of Fracture, my open-source PyQt6 web
  pentesting suite. Verified every module imports clean, the app builds all its
  tabs, and the core intercepting proxy works end-to-end — pushed a live
  request through it and confirmed the response came back and got logged. Also
  verified the HTTPS interception path generates its CA and per-domain leaf
  certs correctly. Full test suite green (14/14).
- Fixed two issues the audit turned up: swapped a deprecated datetime call in
  the cert code for the timezone-aware form (tests now run warning-clean), and
  documented the optional WebEngine dependency the embedded browser tab needs
  so it's no longer a silent gap in the install.

## 2026-07-21
- Polished the two-factor code input on my self-hosted VPN's admin dashboard.
  The 6-digit field had been rendering as an unstyled default input right next
  to a properly styled password field, so I gave it a purpose-built treatment —
  large centered spaced monospace digits with a focus ring matching the brand
  accent — while keeping the numeric keypad and one-time-code autofill hints
  intact. Deployed and verified against what the browser actually serves, not
  just the source file.
- Wrote a complete architecture-and-rebuild reference for that VPN box, built
  from the running system rather than memory: the mesh networking, the
  hand-written firewall, SSH hardening and port-knocking, the DNS ad-blocker,
  the dashboard and its 2FA/session auth, the honeypot data pipeline, the ~20
  self-monitoring scripts, log-shipping, encrypted backups, and an ordered
  from-scratch rebuild runbook — every secret reduced to a "where it lives / how
  to regenerate" pointer with no values. The goal was a single document I could
  rebuild the whole box from by hand.
- Extended that reference to cover the two machines the VPN box talks to but
  doesn't run: the honeypot VM and the NAS. Documented the honeypot end-to-end —
  the containerized SSH/telnet trap, its fake-server persona and accept-anything
  credential policy, and the shipper daemon that tails its logs, adds geolocation,
  and streams events to the dashboard with lossless retry — plus the NAS's three
  roles (battery/UPS reporting, an append-only log sink, and a locked-down
  forced-command backup receiver). Also wrote a full panel-by-panel rundown of the
  dashboard itself, not just its login. The result documents the whole system
  from three vantage points instead of one.
- Rendered that reference doc to a self-contained HTML page and self-hosted it on
  my private, network-only pages server — a small static-site host I run behind
  the VPN — so the whole writeup is browsable in-place rather than living as a
  loose file. Converted with an off-the-shelf markdown tool, wrapped in a minimal
  responsive shell (light/dark, scrollable tables and code), and kept deliberately
  off the public web since it's internal infrastructure detail.
