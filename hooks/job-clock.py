#!/usr/bin/env python3
"""
The job clock — the reset half of WALL 4 (the box gate).

Fires on UserPromptSubmit. Every time Divya says something, it stamps the clock.

`agent-guard.py` reads that stamp: if more than BOX_HOURS have passed since she last
spoke, agent/workflow dispatch is BLOCKED until she speaks again.

PER-SESSION since 2026-07-15: her message stamps BOTH the global clock and a
per-session clock (.job-clock-<session_id>). The box gate prefers the per-session
stamp, so talking in one window no longer un-boxes every other window on the
machine — a runaway background lane stays boxed until she speaks in THAT session.

This is split into its own hook on purpose. The reset must be something the model
CANNOT do to itself — otherwise it is not a box, it is a suggestion. The only key that
opens Wall 4 is a human turn.

(Bypass for genuinely unattended runs: touch ~/.claude/.allow-long-run)
"""
import json
import re
import sys
import time
from pathlib import Path

CLOCK = Path.home() / ".claude" / ".job-clock"


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    sid = re.sub(r"[^A-Za-z0-9_-]", "", str(payload.get("session_id", "")))[:64]
    stamp = json.dumps({"last_user_turn": int(time.time()), "session_id": sid})

    try:
        CLOCK.parent.mkdir(parents=True, exist_ok=True)
        CLOCK.write_text(stamp)
        if sid:
            (CLOCK.parent / f".job-clock-{sid}").write_text(stamp)
        # prune per-session stamps older than 7 days so they don't accumulate
        cutoff = time.time() - 7 * 86400
        for p in CLOCK.parent.glob(".job-clock-*"):
            try:
                if p.stat().st_mtime < cutoff:
                    p.unlink()
            except OSError:
                pass
    except OSError:
        pass  # never break a user's turn over our own bookkeeping

    sys.exit(0)


if __name__ == "__main__":
    main()
