#!/usr/bin/env bash
# Nightly devlog push. Commits only if there's a change; scans before
# committing so a secret never even becomes a commit; alerts and pauses
# (exits non-zero, pushes nothing) if the scan trips.
set -uo pipefail
REPO="/home/dev/Desktop/Dev/devlog"
cd "$REPO" || exit 1
LOG="$REPO/.push.log"

# Nothing changed? done.
if git diff --quiet && git diff --cached --quiet \
   && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    exit 0
fi

# Scan before committing — the safe gate.
if ! python3 "$REPO/scan-secrets.py" DEVLOG.md >>"$LOG" 2>&1; then
    echo "$(date -Iseconds) PAUSED: scan found sensitive data" >> "$LOG"
    notify-send "Devlog push PAUSED" \
        "scan-secrets flagged DEVLOG.md — review before it ships" 2>/dev/null || true
    exit 1
fi

git add -A
git commit -q -m "devlog: $(date +%F)" || exit 0
if git push -q 2>>"$LOG"; then
    echo "$(date -Iseconds) pushed $(git rev-parse --short HEAD)" >> "$LOG"
else
    echo "$(date -Iseconds) push failed (see above)" >> "$LOG"
    notify-send "Devlog push failed" "check $LOG" 2>/dev/null || true
    exit 1
fi
