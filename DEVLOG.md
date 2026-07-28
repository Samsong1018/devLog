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

## 2026-07-24
- Added test coverage for a security control that was flagged as missing
  after an earlier fix to a P2P file-sharing app's relay fallback path.
  When direct peer-to-peer fails and traffic has to relay through a
  signaling server, the key exchange for the encryption is no longer
  implicitly trusted — both sides derive a short human-readable code and
  a person has to confirm the codes match before any data moves, closing
  off a man-in-the-middle risk. That confirmation gate itself had zero
  test coverage (only the underlying cryptographic math was tested).
  Wrote tests that drive the actual gate through the app's real public
  API against a lightweight fake network/WebRTC harness: confirming
  proceeds and sends data, rejecting aborts with nothing sent, canceling
  mid-wait tears everything down cleanly, and going 120 seconds without
  a response is treated as a rejection rather than hanging indefinitely
  or silently proceeding. Test suite went from 79 to 99 passing tests,
  type-checked clean, no regressions.
- Closed out the remaining items from an earlier infrastructure audit on
  my self-hosted VPN box. Verified two previously-flagged items were
  actually already fixed (an integrity monitor's watch list and its
  re-baselining), corrected the stale note that said otherwise, then
  cleaned up the two real leftovers: removed a handful of stale debug
  backup files sitting in a backend directory, and disabled an unused
  network service (an NFS-related dependency with no actual NFS mounts
  anywhere on the box) after confirming nothing depended on it.

## 2026-07-26

- Started CyberGame, a cybersecurity learning game that isn't a flashcard
  app. I've built the quiz-app version of this twice now and both times it
  drifted into rote pattern-matching, so this time I did the research
  first. Ran four parallel research passes (current cert exam objectives,
  the existing landscape of hacking games and training platforms, twenty
  game-design concepts across twenty genres, and an eight-way architecture
  comparison) and turned the output into a design brief plus a 388-line
  build checklist with 185 checkboxes and eleven go/no-go gates.
- The concept inventory came out at 748 tagged rows across sixteen
  knowledge territories, plus a seventeenth "gap layer" for the stuff no
  certification actually tests: reading a log format you've never seen,
  knowing when *not* to escalate, ticket hygiene, saying "I don't know,
  here's how I'd find out." Tagged every row as inert, hybrid, or
  procedural. About 72% is procedural, meaning it has a decision or a
  cause-and-effect chain in it rather than being pure memorization. Cert
  prep products ship roughly the inverse ratio, which is the opening.
- Two design decisions I'm fairly confident about. It's one game with
  eight mechanics rather than eight games, because a concept only counts
  as learned once it survives in two different mechanics, and separate
  games can't share that evidence. And answers get computed rather than
  written down wherever a program can derive them (hashes via WebCrypto,
  certificates via a real ASN.1 parser, CVSS via the published formula),
  because wrong information in a security study tool is worse than no
  tool at all.
- Also went with plain HTML/CSS/JS over a game engine. It's a game made
  of documents, terminals, logs and graphs, which is exactly what the DOM
  is good at, and an engine's actual strengths would go unused while
  costing me text selection, deep links, and a payload small enough that
  someone can click a link and be playing in five seconds.

- Started building the cybersecurity game I designed earlier, and got from an
  empty directory to something playable. It's a SOC triage desk: messages
  arrive, you have a clock, a rulebook that grows as you work, and three calls
  you can make. Looking something up in the rulebook costs a few seconds of
  clock, so it's never blocked, just slower than knowing it.
- The design rule I'm holding myself to is that answers get computed, never
  written down. SPF, DKIM and DMARC results, alignment, lookalike domains and
  the correct verdict are all derived from the message itself by a verifier
  module. Content can't be quietly wrong about something a program works out,
  and wrong information in a security study tool is worse than no tool. The
  message generator declares what verdict the verifier must reach and throws if
  it doesn't, so a mislabelled phishing email is a loud build failure instead of
  silent rot. Checked that across 36,000 generated messages.
- The mechanic is built around the two things email triage training usually gets
  backwards. A DMARC pass isn't a claim about intent, because an attacker who
  registers their own lookalike domain gets flawless authentication on it. And a
  DMARC fail isn't proof of malice, because forwarders break SPF constantly.
  Both are reachable in play, and over-fitting to either one makes you lose.
- Kept the core logic completely free of DOM, storage, and any nondeterminism,
  enforced by a CI check rather than by good intentions. That bought me a
  headless simulator that plays thirty shifts with a synthetic player, and it
  immediately earned its keep by catching two scheduler bugs that no unit test
  would have found: shifts were coming out one item long because a scheduling
  bucket was gated on a tier that's unreachable early on. Fixed, and it went
  from 32 items across 30 shifts to 270.
- Six real bugs total, five caught by tests rather than by reading the code. My
  favourite was a spaced-repetition bug where indirect credit reset a concept's
  decay clock all the way to "just reviewed", which would have quietly let you
  keep prerequisites fresh forever without ever actually being asked about them.
- Next step is deliberately not more code. Five real sessions across five
  different days, then answer honestly whether I wanted a sixth. If the core
  loop isn't fun, adding the other seven mechanics won't rescue it.

## 2026-07-27

### CyberGame

- Played the first round and immediately found a bug from the player's seat,
  which is the entire argument for playtesting your own tool. The message was a
  lookalike domain — same brand, wrong TLD — carrying a macro-enabled Excel
  workbook from a sender that failed DMARC. Two critical findings. I read it as
  two red flags, which was correct.
- The bug: the game was offering "macro-enabled attachment" as a *wrong* answer
  on a message that carries a macro-enabled attachment. The check that fired was
  the "macro attachment from an unauthenticated sender" variant, and the code
  that builds the wrong-answer list was filtering on exact matches only, so the
  plainer version of the same fact slipped through as a distractor. About half
  of all generated instances hit it.
- That's the worst failure a study tool can have. It doesn't just fail to teach,
  it teaches the negation. Fixed by having the analyser return every finding
  code that is *literally true* of a message — a wider set than the findings that
  drove the verdict — and building distractors against that instead.
- Found a second one while I was in there: the answer list was seeded from
  whichever check happened to run first rather than the one that decides the
  call, so the correct answer was only present by luck. Both the grader and the
  option list now share a single definition of what counts as acceptable, so
  they can't drift apart.
- Also: the game no longer starts the moment the page loads. The shift clock
  runs on wall time from the start of a shift, so opening the tab was quietly
  spending your seven minutes while you read the header. There's a start screen
  now. Enter begins it, so the whole loop stays keyboard-only.
- Five regression tests added, 82 total, all gates green.

### CyberGame — the second mechanic

- Built the terminal drill. The reasoning for doing it now wasn't just content
  variety, though that was the trigger: with only one mechanic, my own rule that
  a concept needs evidence from two different mechanics before it counts as
  learned was unreachable by construction. It was decorative. Now it isn't.
- The shell is a real shell. Input gets parsed into a syntax tree rather than
  string-matched, then executed against a seeded, immutable filesystem with real
  owners, permission bits and setuid flags. Pipes, redirection, `&&`, and globbing
  across multiple path components all work.
- Flags are implemented, not tolerated. Searching for files with *at least* the
  setuid bit set and searching for files whose mode is *exactly* setuid are
  genuinely different searches that return genuinely different results, because
  that difference is the entire content of one of the concepts. If the game
  quietly treated them the same, it would be teaching the opposite.
- No tab completion, deliberately. The flag you cannot remember is the thing
  being trained, and completion hands it straight back.
- Ten drill goals, every answer computed by walking the generated host. No
  content file contains a path. The generator refuses to hand out a drill whose
  question has no answer — which paid for itself when it caught exactly that
  mid-simulation.
- Result and approach are scored separately, because typing the answer out by
  hand and running the right search produce byte-identical output and are not
  the same answer. The fix-it drills diff the host before and after, so
  "removed the bad permission" is distinguishable from "removed the bad
  permission and broke three other things on the way past".
- The bit I'm happiest with: three of the drills teach *email* concepts. You
  grep a mail log for the sender pretending to be the client, and every fake in
  that log passes authentication perfectly — so filtering on authentication
  failure gives you a confident, complete, wrong answer. Same lesson as the
  triage desk, different verb. Those are what let anything reach "learned".
- Six bugs found building it, two by the headless simulator rather than by
  tests. One was a bug I had already fixed once and reintroduced, which is its
  own kind of lesson. Another was a generator that produced an unanswerable
  question about one time in two hundred — rare enough to pass every sweep,
  common enough to strand someone mid-shift.
- Content roughly doubled: 23 concepts, 23 templates, 36 graph edges, 122 tests.
  A hundred and twenty simulated shifts now touch every concept with nothing
  starved.

### CyberGame — a debrief that taught nothing

- Playtested again and got one wrong. The sender's domain was a homoglyph of
  the client's — one character swapped for a character that looks like it. Fair
  enough. But the explanation afterwards printed the real domain and the fake
  one side by side, and in a monospace font they are *identical*. Being told the
  answer taught me nothing, which is about the worst thing a study tool can do.
  Nearly half of the generated homoglyphs used that particular substitution.
- Fixed by having the checker work out which character actually moved and name
  it in words rather than showing it. It now says which position, and spells out
  that one is a letter and the other is a digit. Handles doubled letters and
  missing hyphens the same way.
- The deeper problem was that there was nothing to compare against. The status
  bar showed the client's name but never their domain, so spotting a
  one-character substitution was a test of eyesight rather than a comparison.
  A real analyst knows their client's domain by heart. It's in the status bar
  now, which turns an unfair item into a fair hard one.
- Third thing from the same screenshot: about one message in seventeen was
  addressed from a person to that same person. Sender and recipient were being
  picked independently. The obvious fix left a residue, because the
  department-filtered pick fell back to "anyone in this department" — putting
  the excluded person right back in whenever their department had one member.
  Forty-four thousand generated messages now, none self-addressed.
- Four regression tests, 126 total. All three of these came from one playtest
  screenshot, which is the argument for playing your own thing.

## 2026-07-28

- Built the vault box. It's a used HP t630 thin client, fanless, 8GB RAM and a
  128GB SSD, and it'll run Vaultwarden plus act as the high-trust anchor for
  AMvpn's security tooling. Ubuntu 24.04 with full-disk LUKS encryption.
- The interesting problem with full-disk encryption is that every reboot needs
  a human at a keyboard to type the passphrase, which rather defeats a
  headless machine in a rack. Solved it with dropbear-initramfs: a tiny SSH
  server that lives inside the initramfs. The machine boots, stops at the LUKS
  prompt, and I unlock it over the network from my laptop. A stolen drive is
  still a brick.
- I deliberately didn't use TPM auto-unlock or network-bound encryption. Both
  let the box unlock itself. TPM means a stolen machine boots on its own.
  Network-bound means whichever server holds the key can unlock the vault,
  which inverts the whole reason I'm moving these roles off my
  general-purpose NAS. The passphrase stays in my head.
- Hardening — key-only SSH, no root login, default-deny firewall,
  automatic security upgrades. One detail worth knowing — Ubuntu reads
  sshd drop-in configs in filename order and keeps the first value it sees
  for each setting, so a hardening file numbered higher than the installer's
  default silently loses. Mine had to sort earlier.
- Also moved sshd off systemd socket activation back to a persistent daemon.
  The socket has a connection-rate trigger limit, and when it trips systemd
  stops the socket outright rather than throttling — which had already locked
  me out once. On a machine I have to physically walk to, that failure mode
  isn't worth the few megabytes socket activation saves.
- Ran the whole hardening pass behind a ten-minute auto-rollback timer, so a
  bad sshd config would heal itself instead of costing a trip to the rack with
  a monitor under one arm.
- Ubuntu's installer had quietly left about half the disk unallocated in the
  volume group. Extended the root volume from 57G to 115G.
- Lesson of the evening: I spent two hours debugging the wrong machine. A host
  I'd assumed was the new box turned out to be my NAS. The new box
  wasn't on the network at all — both interfaces were administratively down,
  which looks different from an unplugged cable if you actually read the
  interface flags instead of assuming.
- Vaultwarden is live on the vault box. Docker Compose, with the Vaultwarden
  container publishing no ports at all — only Caddy can reach it, over an
  internal bridge network — and Caddy bound to the box's mesh address
  specifically rather than to everything.
- Real Let's Encrypt certificate via a DNS-01 challenge through Cloudflare.
  Worth understanding why that matters: the usual HTTP-01 challenge needs a
  port open to the internet. DNS-01 just creates a temporary TXT record and
  deletes it, so the machine gets a publicly-trusted cert while remaining
  completely unreachable from outside. Every client trusts it, nothing is
  exposed, no CA to install on my phone.
- Built the Caddy image locally from the official builder plus the official
  Cloudflare DNS plugin instead of pulling a community image. A box holding
  every password I own isn't where I want binaries from an unvetted registry.
- Picked a deliberately boring subdomain. Certificate Transparency logs are
  public and permanent, so anything you get a cert for is announced to the
  world. Naming it "vault" would advertise exactly what it is.
- Disabled the admin panel rather than configuring it. Its token is an Argon2
  hash containing dollar signs, which Docker Compose interpolates and silently
  breaks — a well-known footgun. I don't need the panel; the one thing I
  wanted from it (closing registrations) is an environment variable.
- Then actually tested that registrations were closed by POSTing to the
  register endpoint and confirming the rejection, rather than setting the flag
  and assuming. Setting a flag and trusting it is how you discover an open
  signup page six months later.
- Nightly encrypted backups to the NAS. Uses SQLite's own .backup command
  rather than copying the file, because copying a live SQLite database gives
  you a torn file that restores as corruption — and you find out on the one
  day it matters. Encrypted with age, so the NAS only ever holds ciphertext.
  Dedicated SSH key for the push, restricted to that one source address.
- Caught something while wiring that up: my first draft put the backups inside
  the NAS's writable network share, where any machine on the LAN could delete
  them. Encryption protects confidentiality; it does nothing for availability.
  Moved them outside the share.
- Measured something I'd been assuming wrong: my VPN is hub-and-spoke, so two
  machines sitting in the same room talk to each other by way of a cloud VM in
  another state. 55ms versus 0.9ms on the local network. Fine for a shell,
  useless for file transfer — so the NAS gets mounted over the LAN at home and
  over SFTP when I'm away, since SFTP handles latency far better than SMB.

- Tracked down why my Raspberry Pi kept falling off the VPN. It'd go quiet
  every so often — box still powered, still running, just gone from the mesh —
  and the only thing that ever fixed it was a power cycle. Turned out the
  watchdog I wrote two weeks ago to fix exactly this was what was causing it.
- The watchdog ran from root's crontab and healed a stale tunnel by taking
  WireGuard down and back up. Cron gives user crontabs a minimal PATH with no
  /sbin on it. wg-quick needs a binary that lives in /sbin, so it died with
  "command not found" partway through bringing the interface back — and
  wg-quick's cleanup trap deletes the interface on failure. So the recovery
  routine destroyed the tunnel instead of restoring it, then retried every
  sixty seconds, failing the same way each time. Only a reboot fixed it,
  because systemd starts the same command with a full PATH.
- Worst part is the arithmetic. The underlying fault was a two-minute blip —
  my VPN hub runs its backup at 3am on a box with under a gig of RAM, and
  every peer goes briefly stale while it does. Every other machine just
  re-handshakes and carries on. The Pi was the only one with a "fix" attached
  to it, and that fix turned a two-minute blip into a seventy-one-hour outage.
- Nearly couldn't diagnose it at all. The same session that added the watchdog
  also "enabled" persistent logging — set the right value in the main config
  file and moved on. Raspberry Pi OS ships a drop-in that sets the opposite,
  and drop-ins win. So logging had been wiped on every reboot for seventeen
  days, and every power cycle destroyed the evidence of why the power cycle
  was needed. Two mistakes from one session, and the second one hid the first.
- What saved it was that the hub logs peer connect/disconnect events and keeps
  months of history. An outside observer survived when the machine's own logs
  didn't. That gave me exact timestamps, and — more usefully — showed that all
  three peers dropped together each time, which immediately moved the question
  from "what's wrong with the Pi" to "what's wrong at 3am".
- Fixed the PATH, moved recovery to restarting the systemd unit so the
  environment comes from systemd rather than cron, and added an escalation
  ladder that ends in a rate-limited reboot — an automatic version of the
  thing I'd been doing by hand. Proved the fix by deleting the interface
  outright and watching it come back on its own in twenty seconds.
- Then rebooted the box specifically to prove the logging fix survived,
  because "I set the config value" is precisely the claim that was wrong last
  time. Also added a flight recorder writing one line a minute, so next time
  there's a record of the run-up and not just the crater.
