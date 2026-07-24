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

## 2026-07-22
- Patched and rebooted the server behind somab.dev to pick up a pending kernel
  security update. Pre-flighted it first — confirmed the reboot was actually
  required and that the site was healthy — then rebooted and verified it came back
  on the new kernel with the web server serving and the site returning 200.
  Downtime was under a minute.

## 2026-07-23
- Closed out a small security backlog from an earlier multi-project audit.
  Two items turned out to already be fixed from an earlier session I hadn't
  logged: a pentest tool's Flask-cookie decoder had a hard cap against
  decompression-bomb payloads, and its Werkzeug debugger-PIN calculator let
  you override the module/class name for apps that don't use a vanilla Flask
  setup (silently wrong otherwise). An integrity-checker script's baseline
  file also turned out to already be HMAC-signed with a key stored outside
  the folder it watches, so tampering with the monitored files alone can't
  forge a clean baseline — verified that one live.
- Fixed the one item that was still open: a period-tracking web app was
  falling back to a random in-memory secret for its CSRF tokens on every
  restart, which meant any open browser tab got logged out of form
  submissions after a deploy. Set a persistent secret in production and
  restarted the service — verified clean startup and that the site still
  loads.
- Built a branded maintenance page for this portfolio site so a server
  reboot shows something better than a raw browser connection error.
  Put a CDN in front of the origin and wrote a small edge function that
  passes normal traffic straight through untouched, and only serves the
  custom "be right back" page (matching the site's real look and feel,
  with a script that auto-reloads once things are back) if the origin
  is actually unreachable or erroring. Wired it as a wildcard so any
  future subdomain gets the same protection automatically the moment
  it's put behind the CDN — no repeat setup needed. Also fixed access
  logging so real visitor IPs still show up correctly now that traffic
  passes through the CDN layer. Tested the whole failure path for real
  by briefly taking the origin down and confirming the fallback page
  rendered before bringing it back up clean.
- Cleaned up my personal shell config: removed a stale alias pointing at a
  path that no longer existed (a broken duplicate of one that already
  worked), dropped an alias for a tool that's been superseded by a newer
  project, and fixed a misplaced section header left over from an earlier
  reorganization.
- Planned out the build for a new piece of self-hosted infrastructure
  arriving tomorrow: a small dedicated machine that'll run a self-hosted
  password manager and take over a few high-trust jobs (integrity
  monitoring, a second backup copy, tamper-resistant logging) currently
  living as stopgap workarounds on a general-purpose box. Worked through
  a genuinely tricky design problem along the way — a password manager
  that also stores your two-factor codes creates a circular dependency if
  you're not careful, since the one account guarding everything else can't
  be gated by a code generated inside itself. Resolved it by keeping that
  one account's second factor independent (phone app plus a hardware key)
  while letting every other account's codes live inside the vault normally.
  Disk encryption strategy for a machine that won't have someone standing
  in front of it to unlock it after a reboot is still being worked out —
  leaning toward hardware-backed auto-unlock if the board supports it,
  otherwise just minimizing how often it needs to reboot in the first
  place.
- Chased down live "API unreachable" errors on my VPN's admin dashboard.
  Root cause: one endpoint was running five unindexed aggregate queries
  against a honeypot events database that had grown past a million rows,
  and on a memory-constrained box that was enough to blow past the reverse
  proxy's timeout on every poll. Confirmed it live in the proxy's error
  log — the same request failing every 30-90 seconds, continuously, until
  fixed. Added the missing indexes; the same query went from about 12
  seconds to 20 milliseconds. Watched the error log afterward to confirm
  the timeouts actually stopped rather than just assuming the fix worked.
- Also did a full pass over three days of unified server logs (auth,
  firewall drops, VPN peer connect/disconnect, app errors) to separate
  normal background internet noise — routine port-scanning, one earlier
  unrelated API blip — from anything that actually needed attention.
- Audited every project for leftover references to an old personal email
  address I'm migrating away from, including checking whether the
  honeypot's GeoIP enrichment pipeline touched it anywhere (it doesn't —
  came back clean). Found and fixed real references in three web apps'
  privacy policy and terms pages, one push-notification config value in
  each, and the site's security contact file. One of the three apps is a
  Next.js project, so that one needed a real production rebuild rather
  than just editing a static file. Consolidated all of the public-facing
  ones to a dedicated project contact address instead of a personal inbox,
  and updated a couple of purely cosmetic SSH key labels on infra boxes to
  match the new personal address. Verified all of it live afterward with
  zero old references left anywhere touched.
