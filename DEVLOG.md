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
- Follow-up: disabled the Pi's onboard WiFi entirely. It had been sitting on
  both ethernet and wireless on the same subnet, two DHCP addresses, two
  default routes to the same gateway. That's ambiguity with no upside on a
  machine that's racked and wired — either address can end up bound to either
  adapter, and the wireless one had power saving on, so traffic could land on
  a radio that was asleep.
- First attempt only half worked. Removing the network profile kept the
  interface down across a reboot, but the radio block silently came back
  unblocked, because the service that restores that state isn't enabled by
  default. So the interface was only down by side effect. Went one level
  lower and disabled the hardware in the boot config instead — now the device
  doesn't exist and the driver never loads.
- That's twice in one night that a change looked applied and wasn't. Same
  lesson as the logging: reboot and re-check, don't trust the state you see
  right after running the command.
- Two things on the VPN today. First, a small one: the dashboard was listing
  connected peers in whatever order they'd been added to the config, so the
  newest box sat at the bottom out of sequence. Fixed it in the API rather
  than the page, since the frontend just renders whatever order it's handed —
  one change covers every client. Sorted on parsed addresses rather than text,
  because as strings ".10" sorts before ".2".
- Second, the real one: my VPN box checks its own critical config files
  against a list of known-good hashes. The flaw is that the list lives on the
  same box it's protecting. Anyone who gets root can change a file, regenerate
  the list, and the alarm never goes off. The box is the only witness to what
  it used to look like.
- So the hashes now get pushed to my vault machine, which stores them
  append-only in a hash chain — each entry sealed against the one before it.
  The key the VPN box uses is locked to a single command: it can add an entry
  and nothing else. It can't read the history back, can't delete, can't get a
  shell. A fully compromised VPN box can still lie about tomorrow, but it can
  no longer quietly rewrite what it said yesterday.
- Tested it as an attacker rather than trusting the design. Tried to get a
  shell with that key, to read the log, to delete it — all three just land in
  the receiver and get rejected. Then took a copy of the chain and edited a
  past entry: caught. Deleted one: caught twice over, by the sequence gap and
  the broken link.
- Also caught myself shipping the same bug for the third time this week: the
  push script merged error output into the value it was checking for success,
  so a harmless SSH warning about terminals made a submission that had
  genuinely been recorded report as a failure. Fixed the check, and wrote the
  pattern down properly this time — diagnostics don't belong in the same
  stream as the thing you're testing.
- Closed the obvious hole in yesterday's integrity work: the checker wasn't
  watching itself, and neither was the script that ships hashes off-box. Both
  are now in the monitored set. Without that, anyone with root could blank the
  checker and the baseline would go on cheerfully reporting clean — the thing
  doing the reporting being the thing they'd just edited.
- Nearly shipped that broken. My "is this already applied?" check searched the
  whole file for a path that also appears in the script's own header comment,
  so it decided the work was already done and changed nothing, while printing
  success. Caught it by expanding the array in a shell and counting entries
  instead of believing the patch script. Fourth time this week I've been bitten
  by matching a loose substring.
- Then went looking at my honeypot database, which had grown to 874MB and
  looked like a runaway. It wasn't. The nightly cleanup was running fine and
  correctly deleting nothing: retention is 90 days and the data only goes back
  84, so there was genuinely nothing old enough to remove. First real deletion
  lands next week. Every page in the file is live data — no bloat to reclaim.
- Two genuine bugs did fall out of looking properly. Retention was quietly 91
  days rather than 90: timestamps are stored with a "T" between date and time,
  the cutoff was generated with a space, and on the boundary day that one
  character sorts the wrong way and every row survives an extra day. Confirmed
  by running the comparison at both cutoffs before and after.
- The second: the write-ahead log had grown to 33MB against a 4MB threshold,
  because the nightly checkpoint used a mode that copies data back but never
  shrinks the file. Worth checking it wasn't the reader-pinning leak I fixed
  earlier this month — it wasn't, a full checkpoint drained it instantly with
  no contention, which a pinned log couldn't have done. Switched the mode.
- Moved my VPN box's nightly encrypted backups out of the network file share
  they'd been landing in. The share is writable and browseable, so every one
  of those backups could be deleted by anything on the network that could log
  in to it. They were encrypted, which protects the contents and does nothing
  at all for whether they still exist. A backup someone else can delete isn't
  a backup. Same fix I applied to my password vault's backups last week.
- Checked first that the destination genuinely isn't exported anywhere —
  there's no point moving files from an exposed directory to another one.
- Two things pointed at the old path, not one: the receiving script and a
  nightly cleanup job in cron. Missing the second would have left a cleanup
  pointing at a directory that no longer exists — which fails silently and
  quietly, and you find out months later when the disk is full.
- Copied and byte-compared all nine files before deleting any originals,
  rather than moving them. Then tested the whole path from the sending side
  with the real key: a push stored correctly and returned the exact string the
  sender checks for, a repeat push was refused as a duplicate, a filename with
  directory traversal in it was refused, and asking for a shell got
  intercepted and refused too.
- Also had to correct something I'd written down earlier. I'd recorded the
  vault backup key on that machine as locked down to a single source address.
  Reading the actual file, it has no restrictions at all — full shell access.
  The neighbouring key is properly locked down, which is probably why I
  misremembered. Left it alone and flagged it rather than quietly changing a
  second backup system in the same sitting.
- Went back over the whole vault build end to end — the vault box itself, the
  VPN hub it depends on, and the NAS it backs up to — to actually verify
  everything was secure and working rather than trusting my own notes from
  the build.
- The unrestricted backup key I'd flagged and left alone last time was still
  unrestricted. This time I built a proper receiving script for it — same
  pattern as an existing one I already trust: validate the filename, refuse
  anything that doesn't match, never overwrite, cap the size — then locked
  the key down to only run that. Tested both directions before calling it
  done: a bad command gets refused, a correctly named file still comes
  through clean.
- A notification script had been quietly logging false failures for weeks —
  it looked like every alert was failing to send, even though the messages
  were arriving fine. Root cause was two different processes racing to write
  the same temporary file. Nothing ever read that file back, so I just
  stopped writing it.
- A honeypot database had wide-open write permissions — any local process
  could've written straight into the forensic record, bypassing the
  application entirely. Tightened it, then confirmed the one process that's
  actually supposed to write to it still could.
- Rebooted the VPN hub for a pending security update and it surfaced a real
  bug: the reverse proxy tried to start before the VPN interface had finished
  claiming its address, lost that race, and sat dead silently for several
  minutes — no dashboard, no monitoring ingest, nothing watching to say so.
  Fixed the startup ordering so the proxy waits on the tunnel, restarted it,
  and confirmed it was actually serving again rather than assuming a restart
  fixed it.
- Right after that reboot I got a wave of file-integrity alerts that looked
  alarming out of context. Turned out to be my own earlier fix — I'd edited a
  script that's on the integrity watch list and forgotten to reset the
  baseline afterward, so it was correctly flagging my own change as
  unauthorized. Checked every other watched file by hand before calling it
  routine, rather than assuming that was the whole story.

### CyberGame — the game was cheating, and I could measure it

- Playtest feedback: you could learn the right answer from a repeating pattern
  instead of from the material. If the body said "forwarded", let it go. If
  there was a macro-enabled spreadsheet attached, escalate. Never had to read a
  single header.
- Before changing anything I built a gate to measure it. It generates thousands
  of messages, then asks how well each *visible cue* — an attachment type, a
  word in the body, the presence of a header — predicts the correct answer on
  its own. It fails the build if any single cue predicts above 85%.
- Nine cues were at 100%. Not two. A macro attachment, the word "forwarded", a
  mailing-list header, a reply-to address, any link at all, a missing signature
  header, a subject line mentioning passwords — each one of those, by itself,
  told you the answer every single time.
- The cause was structural and it was mine. Messages were built from eleven
  templates, each with a fixed correct answer baked in and a distinctive
  surface. So the surface predicted the answer. The generator was authoring the
  answer, which is exactly the thing the project's own rules forbid.
- Rewrote it so a message is assembled from independently drawn parts — who sent
  it, how it travelled, what it carries, how it's worded — and the answer is
  whatever the checker derives from the combination. A template is now allowed
  to fix at most one of those. Same spreadsheet, three different correct answers
  depending on who sent it.
- That surfaced a real error I'd shipped. Any message claiming to be from the
  client's own domain that failed authentication was being flagged as a critical
  spoof — including a perfectly legitimate mailing-list message from a sender
  with no signature on that path. The game was teaching people to escalate their
  own colleagues' forwarded mail, which is the precise opposite of one of the two
  lessons it's built around. Now it distinguishes "failed with no explanation"
  from "failed and there's a forwarder right there in the headers".
- Every cheap cue now sits between 42% and 54%, against a 38% baseline for just
  guessing the commonest answer. Two cues still predict perfectly and I've
  allowed them explicitly with written reasons, because they're true rules
  rather than artefacts of how I generate messages: an executable attachment,
  and a credential-harvesting page on a domain unrelated to anyone involved.
  Both are deliberately rare.
- 131 tests, three of which assert the property directly rather than testing a
  specific case: a fixed feature has to produce more than one answer, forwarded
  mail has to be both released and held, a macro has to reach all three verdicts.

### CyberGame — it's a desktop now

- The last fix stopped you being able to guess the answer from a surface cue.
  What was left was the shape: a verdict button above a list of radio options is
  a quiz, however good the reasoning underneath it is.
- So it isn't a screen of questions any more, it's a workstation. A menubar, a
  pinned ticket queue down the left, a dock along the bottom, and four apps —
  shift status, mail, terminal, runbook. You clock in, a queue of tickets lands,
  you open one, it opens in whichever app it needs, you work it and close it.
- The mechanics didn't change at all. Both of them already took "here is an
  element, mount yourself into it", so a window is just a different element.
  That interface was written months of decisions ago and it's the only reason
  this was a cheap change rather than a rewrite.
- The ticket queue is a new surface, and everything I learned last week says a
  new surface will get learned if it carries information. So ticket titles are
  built only from things already measured as telling you nothing, priority is
  drawn from the random seed and is deliberately uncorrelated with severity, and
  the module that builds tickets is structurally unable to read the answer. A
  test asserts that two messages with opposite correct answers produce identical
  tickets, and the tell detector now watches the queue too.
- Priority being frequently wrong is realistic, incidentally. Learning not to
  trust the queue's opinion is a genuine skill rather than a simulation artefact.
- Caught one thing before it shipped: the desktop's main pane and the message
  views were both going to use the same CSS class name, which would have quietly
  restyled the inside of every email.
- The shell went from one file to seven and had no tests at all, so I added a
  DOM test harness and thirteen tests that drive the whole loop — clock in,
  queue fills, ticket routes to the right app, verdict submits, queue empties,
  summary appears. Writing them found two real bugs, including one where the
  page's own HTML had been silently turned into a function call.
- 150 tests. Next is the difficulty ramp: policy memos that arrive as email and
  change what the correct answer is.

### CyberGame — free-floating windows

- Looked at the tiled version and didn't like it, so it's real windows now.
  They open, drag, resize, stack, minimise and close, and the dock works like a
  taskbar — click an app to open or raise it, click the focused one to minimise.
- The tiled layout had existed for one specific reason, which I'd written down
  at the time: both of the game's views listened for keystrokes globally, so two
  of them on screen at once would mean typing "1" into a terminal also casting a
  verdict in a mail window behind it. Tiling made that impossible by only ever
  having one view alive.
- So the actual fix came first. Each view now listens on its own element, which
  means a keystroke only reaches the thing that has focus — the rule every real
  desktop uses. That makes focus load-bearing rather than decorative: raising a
  window has to genuinely move focus into it, and now does. There's a test that
  puts two views side by side, types into one, and asserts the other didn't move.
- Two bugs surfaced that were only reachable once two windows can exist at once.
  Every window carried the same element IDs, which is invalid HTML and means any
  lookup can find the wrong window's controls. And focusing a new window focused
  its first button — which the triage view deliberately ignores number keys on,
  so opening a mail window was silently killing its own keyboard shortcuts.
- Windows can't be dragged off screen, won't shrink below a usable size, and
  re-clamp if the browser resizes. On a narrow screen there's no floating at
  all — dragging windows around a phone is miserable.
- Desktop tests went 13 to 21, including drag tracking by exact pixel deltas and
  the focus-isolation one. 158 total.
- Went hunting for a rack mount to hold a small PC and a couple of Pi boards
  side by side in the same slot. The commercial options didn't actually add
  up — one popular "10-inch" Pi rack format and the real half-rack standard
  aren't the same width, despite looking similar in listings, and stacking
  two of them would've overrun a standard rack opening by more than an inch.
  Worth doing the math before ordering rather than after.
- Decided to just design the bracket myself instead — one part sized for the
  whole slot, then split down the middle for printing, so both halves share
  the exact same bolt-hole positions instead of hoping two separately-bought
  parts happen to line up.
- Wrote it as parametric code rather than a fixed model, so the numbers (rack
  dimensions, mounting hole spacing) are named variables instead of buried
  magic numbers — easy to tweak once, everything downstream updates.
- First render caught a real design mistake: I'd built the rack-mounting ears
  flat, with the screw holes drilled straight down. Real rack rails are
  vertical, so the ears need to stand up on edge with the holes drilled
  sideways, front to back. Would've been obvious in person and completely
  wrong once actually installed — caught it from a screenshot before it
  wasted anyone's filament.
- Second render caught a subtler one: a wall that was supposed to sit on a
  floor was only mathematically touching it, not overlapping it — a classic
  CAD trap where two surfaces meet at a perfect seam with zero shared volume,
  which can print as a hairline gap or a weak, barely-attached joint instead
  of one solid piece. Fixed by giving every part that touches the floor a
  small deliberate overlap instead of a flush touch.
- Neither bug was one I could catch alone — I don't have the CAD tool
  installed on this machine, so the whole loop ran on someone else rendering
  and sending back a screenshot. Good reminder that "looks right in the code"
  and "is right" aren't the same thing when you can't actually see the part.

## 2026-07-29

### CyberGame — the rules change on you now

- The difficulty ramp is in. Every few shifts a policy memo lands on the clock-in
  screen: your employer has changed what they want done about something. You
  can't start the shift until you've acknowledged it, because a rule change
  nobody read is indistinguishable from no rule change.
- The interesting part is what it forced me to separate. Severity used to be
  hardcoded — a lookalike domain *was* an escalation. But that's two different
  claims wearing one hat. "This domain is a homoglyph of the client's" is a
  fact you can compute. "We escalate those rather than holding them" is a
  decision somebody made, and decisions change. Those live in different files now.
- The line that must not be crossed: a policy can change the call, never the
  evidence. It can say "hold archives this week"; it can't say "treat this as
  though it failed authentication". There's a test asserting that under every
  version of the rules, the findings and their details are byte-identical — only
  the weight attached to them moves. And the debrief always tells you both, so
  you can see the evidence didn't change even when the answer did.
- One memo is temporary and expires, which announces itself too. A heightened
  posture nobody stands down is a real thing that happens to real teams.
- Writing the memos turned out to be a design problem rather than a writing
  problem, and the tell detector caught two bad ones before they shipped. My
  first attempt re-weighted the two most common findings and collapsed one of
  the three possible answers from 28% of cases to 7% — the game became "escalate
  everything". My second attempt made "authentication failed" predict escalate
  90% of the time, which would have quietly destroyed the one lesson the whole
  thing is built around: that failing authentication is not the same as being
  malicious. Both reasons are now comments in the file so I don't re-add them.
- The gate now runs against every version of the rules, and separately fails any
  version where guessing the commonest answer beats reading the evidence.
- 171 tests.

## 2026-07-30

### CyberGame — running a gate that had never been run

- Two bits of debt I'd flagged and kept not doing. Neither needed a decision
  from anyone, which is exactly why they were the right things to pick up.
- The first: my content pipeline is "fail-closed" — it's supposed to refuse to
  build if a concept is malformed, if a prerequisite graph has a loop, if
  something cites a source that isn't there. It had never once been shown to
  refuse anything. Every other check in the project guards something a test can
  watch go wrong. This one guards whether bad content ships at all, and it had
  no evidence behind it.
- So now there's a test that feeds the real scripts deliberately broken content
  and checks they reject it *for the right reason* — exiting with an error for
  some unrelated reason would have passed a weaker test than I wanted. Sixteen
  cases, including a claim that cites a source it doesn't have, which is the one
  the whole "never assert what you can't back up" rule rests on.
- Two of the cases check it *doesn't* reject things: an empty content folder is
  a normal state early on, and two concepts marked as contrasting with each
  other is not a loop. A gate that fails on the wrong things is a gate someone
  eventually switches off.
- It all passes. Good, but I'd rather know than assume.
- The second: I'd never measured test coverage. The target was 80% on the
  scheduling and mastery code; it's actually 100, 100, 99, 99. Fine.
- The useful number was somewhere else entirely. The file holding my save-file
  validator came back at zero percent — the function that decides whether a save
  is safe to load had never been executed by a test, and neither had the import
  itself. That's the entire restore path, and the failure mode is somebody
  losing all their progress.
- Testing it found a real bug. Imported records were being written without the
  key the lookup filters on, so they'd silently vanish from an append-only log
  that's specifically designed never to lose anything. The browser storage
  backend didn't have the problem, which meant the same save file behaved
  differently depending on which one you were using. That's the part that
  actually worried me.
- 224 tests.

## 2026-07-31

### CyberGame — pacing, and two scheduler bugs behind it

- Asked for this to feel more like Papers Please: one or two new things a day
  rather than everything at once. The first shift was introducing nine concepts,
  which is a firehose, not a day at work.
- Capping it at two was the easy part. The interesting part was that capping it
  didn't work — new material still stopped arriving for stretches of sixteen
  shifts, and finding out why turned up two real bugs in the scheduler.
- The first: my selection weights read as proportions — 45% of the pool should
  be due material, 25% new, and so on — but they were being applied to each
  candidate individually. So a bucket's influence scaled with how many things
  happened to be in it. Late in a playthrough the "revisit" bucket holds twenty
  concepts against the "new" bucket's two, which meant new material was getting
  a twentieth of the share it was supposed to. Normalising per bucket is what
  the numbers always claimed to mean.
- The second was better. A concept you'd been introduced to but hadn't yet
  practised was in *no* bucket at all — one bucket starts at "practised", one is
  for "never seen", and "introduced" fell in the gap. It could only come up if
  it happened to fall due. So the single thing standing between you and new
  material was the single thing the scheduler had no way to choose to work on.
  There's now a bucket specifically for those, on the principle that the fastest
  way to have something new tomorrow is to finish teaching the thing in the way.
- Result: a steady two new concepts a shift, and everything introduced by day
  nine or ten instead of day thirty.
- Also: the policy notices that change the rules only ever appeared on the
  clock-in screen, so you couldn't re-read one halfway through the shift it
  applied to — exactly when you'd want to check. They're mail, so they're in the
  mailbox now, alongside the end-of-shift briefings, each saying whether it's
  currently in force or has lapsed.
- And a test-harness flaw worth writing down: a failing test used to *hang* the
  suite rather than fail it, because cleanup sat at the end of each test body
  and an assertion throwing skipped it, leaving a timer running. Moved cleanup
  to run unconditionally. It now fails in 46 milliseconds where it used to run
  until the timeout killed it. I hit this for real while verifying something
  else, which is how it got noticed.
- 227 tests.

### CyberGame — a third mechanic, and the pattern I nearly built twice

- Two mechanics wasn't enough, and not for the reason I expected. A concept only
  counts as retained once you've been tested on it two different ways, so with
  two mechanics most concepts were stuck one short. 23 of 27 sat at "practicing"
  indefinitely. A third mechanic doesn't add to the library, it unlocks the one
  I already have.
- The new one is an artifact inspector: certificates, tokens, and HTTP response
  headers. The shape is deliberately different from the other two. The mail desk
  asks for one decision plus the evidence behind it. The terminal asks you to
  produce the answer. This one asks you to *enumerate* — tick everything wrong
  with this, and nothing that isn't.
- It's scored on precision and recall separately, which matters more than it
  sounds. Ticking every box catches 100% of real defects and still scores under
  half, because a report full of invented findings costs the next person the time
  to disprove them. Ticking nothing never invents anything and scores zero. There
  is no lazy strategy that survives both numbers.
- Everything is a real artifact rather than a description of one. A certificate
  gets genuinely encoded and then *parsed back from those bytes* to be graded. A
  token carries a real HMAC that gets recomputed. I wrote SHA-256 and HMAC by
  hand for this — the browser's built-in crypto is asynchronous, and the pure
  core of this project is synchronous, so using it would have spread promises
  through every caller.
- One limitation I wrote into the file rather than quietly leaving: the key
  inside a generated certificate is a number of the right size, not a real RSA
  key. Key size is the thing the drill inspects and bit length is exactly how
  you'd measure it for real, and nothing checks a signature against it, so a real
  keypair would buy realism and no correctness.
- **The mistake.** My first version planted exactly one flaw per artifact. A test
  asking for a two-defect example couldn't find one in 200 tries, which is how I
  caught it. That's the same archetype problem I had to rewrite the mail
  generator out of a week ago: if there's never more than one thing wrong, "find
  something, then stop" wins without understanding any of the checks. Worse, the
  scoring *rewards* stopping early, because there's never a second thing to miss.
- Rewrote it so each property is drawn independently — a certificate's expiry,
  its lifetime, its key, its signature algorithm, its issuer, its CA flag and its
  hostnames are seven separate coin flips. Now about a third come out clean, a
  third have one problem, and a quarter have two or more. That spread is pinned
  by a test, with loose bounds so it survives someone retuning a weight later.
- Three real bugs on the way: a certificate that was supposed to be clean could
  have a start date in the future (a short lifetime with a long time remaining
  hasn't begun yet); two flaws could be planted when only one of them is
  findable, putting a lie in the generator's own records; and the hostname
  extension parsed as empty because I hadn't stepped through one layer of
  wrapping — which looks identical to an extension that parsed fine and contained
  nothing.
- A test I weakened on purpose, which I want on the record because it's the kind
  of thing that's usually cheating. One test asserted a shift contains at least
  five items. Inspecting a certificate honestly takes longer than reading a mail
  header, so the count dropped to three — at 90% of the time budget. The count
  was a proxy and had become a misleading one. It now asserts the thing the code
  actually promises: the queue stopped filling because nothing else fits. My
  first attempt at that assertion was too strong and failed, correctly.
- 227 to 257 tests. Eight new concepts, taking the library to 35.

### CyberGame — a question I made unanswerable, and a clock to fix it

- Playtest question that landed: *how are you supposed to know whether a
  certificate has expired or hasn't started yet?* You weren't. That one's mine.
- Both are claims about a date relative to *now*. The panel showed the two
  boundary dates and nothing anywhere on the desk carried a date — the top bar
  had a shift counter and a countdown timer, that's it. So the grader could work
  out the answer and the player structurally could not.
- Which is a specific kind of mistake worth naming. The rule I hold this project
  to is that every answer must be *computed*, never authored. I checked that.
  What I didn't check is that it's computable **by the person being asked**. An
  unanswerable question isn't a hard question, it's a broken one.
- Fixed by putting the reference instant at the top of the decoded panel —
  exactly the moment the grading compares against, so what you see is what's
  being judged. Still no relative phrasing anywhere: "expired 53 days ago" would
  be handing over the verdict rather than the evidence for it. The comparison
  stays yours; you just have both numbers now.
- The test asserts answerability rather than markup. The instant is present, it
  equals the one the grader uses, both bounds are readable, and moving the clock
  the direction that should clear the defect does clear it — so if that row ever
  stopped mattering, the test fails.

### CyberGame — a desk clock, and a terminal that doesn't list everything it does

- Follow-up ask: put the date in the top bar like a Linux desktop panel. Two
  things had to be fixed first before that was even honest.
- The weekday in the top bar came from the *shift number*, not the date, so
  shift 5 was labelled "Tue" whatever day it actually was. Putting a real date
  next to that would have been a visible contradiction. Weekday now comes from
  the date; the shift field just says "shift 5". The countdown reads "6:12 left"
  so it isn't mistaken for a wall clock sitting right beside one.
- And the clock only *ran* during a shift. The single timer in the whole app
  started at clock-in, so off shift the date sat frozen at whenever the page
  loaded. The desktop owns a permanent tick now, torn down with it — a timer
  outliving the thing it draws into is how a failing test turns into a hanging
  one, which I've already been bitten by on this project.
- Went with UTC, partly because a security operations desk genuinely runs on it,
  mostly so the two places showing a time agree instead of being an offset apart.
- Then easter eggs in the off-shift terminal: neofetch, fortune, cowsay, sl,
  sudo, xyzzy, matrix, the vim-versus-emacs argument, and a few that just say no.
  Two rules I wrote into the file: nothing gives away a drill answer, and nothing
  lies about a real command. sudo fails the way sudo actually fails. `rm -rf /`
  refuses the way the real one refuses. If you meet these outside the game later,
  nothing should surprise you. `help` admits the list is incomplete and stops
  there — being shown where they are isn't finding them.
- **Then I immediately made the same mistake I'd just finished fixing.** Wired
  the terminal's `date` to the system clock while the top bar used the game's
  clock, and in the test harness they came out half a day apart. Two clocks
  disagreeing — the exact defect from an hour earlier, in a brand new surface.
  Same lesson as the other repeat I hit today: fixing a class of bug in one place
  does not carry to the next place. You have to go looking for it again.
- One clock is now exposed for everything downstream to read, with a test that
  the two agree, and a second test that walks every easter egg checking none of
  them prints something a drill expects you to have earned.
- 263 tests. I verified both new regression tests fail with only their own fix
  reverted, rather than trusting that passing meant anything.

## 2026-08-01

### CyberGame — a gate for the bug my gates couldn't see

- Yesterday's playtest found a question the player couldn't answer: a certificate
  was graded expired-or-not against "now", and nothing on screen showed what
  "now" was. Fixed it then. Today I went looking for why *every* check I have
  passed while that shipped.
- The answer is that all of them reason about the content and the code. The rule
  this project lives by is that answers must be **computed, never authored** —
  and I'd been enforcing that on the thing doing the computing. But the rule has
  two halves. The answer has to be derived, *and* every input to that derivation
  has to be visible to the person being asked. Only the first half had a gate.
- Which is a nasty class of bug, because from inside a test suite an unanswerable
  question looks exactly like a hard one. The grader agrees with itself perfectly
  either way. Nothing is inconsistent. It's just impossible.
- So: a new check that generates hundreds of items per mechanic, runs the real
  grader, renders the real UI, clicks everything a player could click to reveal
  more, and asserts the evidence behind every finding is actually there in the
  text. Evidence behind a toggle counts — expanding full headers is a real thing
  an analyst does. Evidence behind nothing doesn't.
- The map of "which finding rests on which evidence" is written by hand rather
  than pulled out of the grader. If I derived it, the gate would agree with the
  grader by construction — which is the exact circular reasoning that let the
  original bug through. It has to be an independent statement of what a player
  would point at to justify a call.
- **Verified it twice, because a new gate that passes immediately proves
  nothing.** Put the original bug back: 55 findings fail. Then broke something
  completely different — the mail client's full-headers toggle — to check it
  wasn't just memorising the one case: 43 fail, because a forwarding judgement
  rests on a mail path the player could no longer reach.
- Results of the sweep: the mail desk is clean, the inspector is clean now. So it
  wasn't systemic, it was one mechanic. The gate exists whether or not it
  recurs, and a new finding with no evidence declared fails the build — you can't
  add a question without saying what would answer it.
- The terminal needed a different question, since a shell has no screen to put
  evidence on. There the equivalent is whether the canonical solution actually
  reaches full marks using only commands the game ships. Worth stating because
  the existing check was weaker — it only confirmed the question *has* an answer,
  and an answer no available command can reach is the same failure in a different
  costume. Swept all 18 goals, all clean.
- **And then I nearly shipped a redundant test.** Wrote one for that, sabotaged
  the solver to confirm it wasn't vacuous, and the failure output revealed an
  existing test had caught it too — one that checks more than mine did. Deleted
  mine, widened the existing one's coverage instead. Finished the hour with one
  fewer test than I started with, which is the right outcome and not one I'd have
  found without deliberately trying to break my own new test.

## 2026-08-02

- Caught the public project logs on my site up to date. They'd gone about three
  weeks stale while the private running log kept growing, so this was mostly a
  transcription job with a sanitization pass on top.
- 33 new entries across four existing project logs, plus a new one for the
  security game I've been building since late July.
- The interesting part of that is what doesn't go in. The password manager box
  lives on a deliberately boring-sounding subdomain, because certificate
  transparency logs are public and permanent, so anyone watching them for my
  domain sees the name forever. Publishing "here is what that subdomain is" on
  my own site would have undone the only thing that name was for. It's described
  by capability instead.
- Same rule for the rest: no addresses, no ports, no usernames, no host keys.
  Ran the secret scanner I built for this repo over every changed file plus a
  targeted grep, and it came back clean.
- One honest status change rather than a flattering one: the voice assistant is
  now marked on hold, not prototyping. Its hardware became a NAS three weeks ago
  and nothing has moved since. A portfolio that only ever says "active" isn't
  telling you anything.
- Fixed the hook that nags me to write these entries, because it just falsely
  nagged me for an entry I'd already written.
- It was checking whether a specific set of file-editing tools had been used on
  the log files. I'd appended to them from the shell instead, which that check
  can't see. So it was inferring "did this file change" from a transcript rather
  than asking the filesystem.
- Now it compares the files' modification times against when the session
  started. That catches every way a file gets written instead of one way.
- The bigger problem was the other direction, and it was silent. Work detection
  also only looked at editing tools, so a session where all the real work
  happened over SSH on a remote box triggered nothing at all. That's most of my
  infrastructure work. Whole evenings could go unlogged and nothing would say so.
- Added shell-command detection for that, kept deliberately narrow. A hook that
  cries wolf gets turned off, so read-only commands are absent from the match
  list on purpose and writes to scratch paths don't count.
- Fails safe: if it can't work out when the session began, it falls back to the
  old behaviour instead of blocking on a guess.
- 24 self-test cases plus all six decision paths driven through the real hook
  with controlled timestamps. The false positive is silent, SSH-only work now
  blocks, read-only sessions stay quiet.

## 2026-08-14

### AMvpn — chasing "rsyslog errors" back to a log-rotation restart and a hardening warning, not a real failure

- Went hunting for the source of recurring rsyslog error reports on my self-hosted VPN box. Turned out rsyslog isn't actually failing — it restarts cleanly every night as part of normal log rotation, and a security scanner (Lynis) flags it daily as "unsafe" purely because the systemd unit is missing a couple of sandboxing directives, not because anything is broken.
- While digging I did find two real, low-severity patterns: a Telegram bot listener that fails for a couple of minutes at almost the same time every day before recovering on its own — traced it to the firewall dropping the far side's connection-close packets after the local connection-tracking entry had already expired — and a DNS resolver throwing occasional upstream failures against one of its providers a few times a day.
- Also caught a stray networking quirk in the kernel log: the box's own internal address showing up as an "impossible" source address on the wrong interface a few times a day. Worth a look, not urgent.
- No actual outages, no failed services, firewall state intact end to end. Good reminder that "the monitoring is throwing errors" and "something is broken" aren't the same claim — worth separating them before chasing the wrong thing.

## 2026-08-04

### AHDev — chasing a vanishing wallpaper back to a script I wrote

- Started as a hardware question: a second monitor was showing spiderweb-line
  artifacts with the glass itself intact. Checked the OS side first before
  calling it physical — EDID reading clean, native resolution locked, link
  status good, no reconnect spam in the kernel log since boot. Signal path was
  fine, which is what let me say with confidence it's damage under the glass,
  not a cable or driver problem.
- Then, trying to just reposition that monitor in display settings, position
  changes stopped sticking and the wallpaper started disappearing. Different bug,
  and it turned out to be mine — a background script I'd written months ago to
  auto-restore desktop icon positions after a monitor change.
- The watcher listens for a "monitors changed" signal and restores icons after
  it fires. Reasonable, except the settings panel fires that signal repeatedly
  while you're actively dragging a monitor around, not once at the end. So the
  script was force-restarting the process that draws the desktop background
  every 7-8 seconds for the entire time I was trying to change anything —
  stomping the in-progress change before it could ever get confirmed, and
  blanking the wallpaper as a side effect of the repeated restart.
- Caught it by lining up two logs side by side: the icon-restore script's own
  output and the desktop compositor's errors, same timestamps, every single
  cycle. Fix was a debounce — wait for the signal to go quiet for a few seconds
  before acting once, instead of acting on every single event in a burst.
- Smaller gotcha along the way: killing the stale process by matching its
  command line killed my own shell instead, because the shell's own command
  line literally contained the text I was searching for. Switched to killing by
  process ID and moved on.

## 2026-08-15

### SENTINEL OS — a content bug that was the same bug the project already had a rule against

- This is a study game built around one rule: a concept can't count as "learned"
  until it's been tested two different ways. The idea is you shouldn't be able
  to pass by recognizing the shape of a question instead of actually knowing the
  material — learned that the hard way from two earlier quiz-app attempts that
  both turned into flashcard memorization in disguise.
- Went looking for what content to add next and instead found a case where the
  rule wasn't actually being followed. Eight concepts — every certificate, JWT
  and HTTP-header concept in the game — only had one mechanic testing them.
  They were capped at "practicing" forever, no matter how well you played,
  because there was no second mechanic to confirm it against. Same failure
  mode the two-mechanic rule exists to catch, just sitting quietly in the
  content instead of in the code.
- Fixed it for the certificate concepts by reusing the real X.509 generator
  that already exists for the certificate-inspection mechanic — same DER
  bytes, same encode-then-parse discipline — and planting a small, fixed set
  of certificates on the hosts used by the terminal mechanic instead. Wrote a
  minimal but real `openssl x509` command for the shell to read them with.
  Had to hand-roll its flag parsing, since the shell's existing flag parser
  assumes short flags cluster together (`-la` = `-l -a`) and openssl's flags
  don't work that way — `-noout` would've silently exploded into five
  meaningless one-letter flags.
- Verified the fix actually did something rather than trusting the diff: ran
  the headless simulator both before and after the change, same seed. The
  default run came back byte-identical either way — turned out it just never
  happened to route through those three concepts in that short a run,
  confirmed by literally stashing the change and diffing. Widened the sim run
  and got the real signal: two-mechanic coverage went from 5 concepts to 8,
  and the number of concepts that never got scheduled at all went from 3 to
  zero.
- Three of the eight were fixed at that point. The other five — JWTs and HTTP
  headers — turned out cheap, same session: reused the existing generators
  again, and since that evidence is plain text instead of a binary format,
  the only new tool needed was a small `base64 -d` for decoding a token.
  Deliberately narrowed one of the five to only test the "algorithm: none"
  case rather than a tampered signature, since actually verifying a
  signature needs a cryptographic operation this shell doesn't have — no
  point pretending a lesson is testable when it isn't. All eight closed by
  the end of the session; every certificate, token and header concept in
  the game now has real second-mechanic coverage instead of being
  permanently stuck half-credited.

## 2026-08-19

- Audited my self-hosted password manager box after a hardening pass and
  caught a real bug: a directive meant for the SSH *server* config had ended
  up in the SSH *client* config instead, which silently broke every outbound
  backup push for 9 straight nights. Confirmed the gap with service logs
  (9 consecutive failed runs, zero valid backups the whole time), fixed the
  config, and verified the next backup actually landed. Same failure shape as
  an earlier incident — a backup pipeline going quiet without an alert — so
  the real fix is a freshness watchdog, not just patching this one instance.
- Cleaned up a self-hosted TOTP app I'd deployed alongside the password
  manager, now that I'm using a different TOTP service — removed the app,
  its isolated Docker network, and its backup timer so nothing keeps trying
  to run against a service that no longer exists.
- Confirmed the box's tamper-evident integrity log is still chaining
  correctly post-hardening, and its firewall is still enabled.

## 2026-08-28

**Root-caused a self-hosted game server that accepted connections and then
silently dropped every one of them.**
- Symptom: the client would reach the server, show its password prompt, then
  fall straight into a generic timeout. No error, no rejection message, and
  nothing written to the server's log.
- The real blocker was an assumption inherited from earlier debugging. The
  server's log file was empty, and that had been recorded as "no diagnostic
  signal available." It wasn't true — the game rotates its log on every
  restart and redirects live output to stdout, so the actual logs had been on
  disk and in the journal the whole time.
- Reading them surfaced a strong suspect: the server was a patch version
  behind the client, and the store's build metadata showed the matching
  server-side patch had been shipped for clients only and never released for
  dedicated servers — so no amount of updating would ever close the gap.
- That suspect was wrong. It was a real, verifiable fact sitting right next
  to the actual problem, which is the most expensive kind of red herring.
  Rather than act on it, I ran a packet capture on the game port during a
  live connection attempt.
- The capture showed the client reaching the server and the server answering:
  eight bidirectional exchanges over about 370ms, then a clean negotiated
  close with no retry from either side. That is not a network failure. It
  ruled out every relay, tunnel, VPN and ISP theory at once, and it ruled out
  the version gap too, since the two sides were clearly talking.
- Actual cause: the connection method. The game registers itself with the
  platform's session layer, and joining through the server browser goes via
  that path. The console's raw connect-by-address command opens the transport
  connection but never completes the session join, so the server negotiates,
  refuses, and hangs up — silently, with nothing written to any log.
  Connecting the supported way worked immediately.
- Ruled out with evidence rather than assumption along the way:
  file-descriptor limits (the classic cause of exactly this symptom),
  interface binding, firewall rules, mods, and hostname resolution.
- Two takeaways. "The log is empty" is a claim, not a premise — it went
  unverified and cost more time than the bug did. And a fact that survives
  every check can still be the wrong explanation; the capture cost one minute
  and saved an evening spent downgrading a client for no reason.

## 2026-09-01

**Found and fixed a silently stale search index behind my personal
knowledge-base search tool.**
- The search script reads from a SQLite full-text index that's supposed to
  stay in sync with several hundred markdown notes.
- Turned out the index hadn't been rebuilt in weeks — nothing was wired up
  to refresh it automatically after the original one-time build. Roughly a
  quarter of the notes were invisible to search as a result.
- Rebuilt it, verified the count matches file-for-file, and added a daily
  scheduled job so it can't silently drift out of sync again.

**Re-audited my self-hosted password manager's backup pipeline after two
prior silent-failure incidents.**
- Wanted to confirm the earlier fixes actually held, rather than trusting a
  fix and moving on.
- Backups have completed clean every night for the past two weeks —
  confirmed from service logs on the box itself, not just "the schedule
  looks right."
- Two items still open from the same audit: no automated alert yet if a
  backup run goes stale again, and the offline copy of the decryption key
  still lives in only one physical location. Both flagged as the next
  things to close.
