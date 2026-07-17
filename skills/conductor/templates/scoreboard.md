---
module: "{{MODULE_NAME}}"
slug: "{{MODULE_SLUG}}"
stale_hours: 48
gate_level: "{{run-ahead|gate-every-phase}}"
current_wave: 1
last_verified_against_git: "{{NEVER or ISO_TIMESTAMP}}"
---

# {{MODULE_NAME}} — Scoreboard

> Single-writer file: ONLY a Conductor invocation edits this file. Phase agents write their own card under `phases/` and nothing else.

## Phase table

| Phase | Name | Wave | Status | Owner / session | Branch | PR | Reconciled |
|---|---|---|---|---|---|---|---|
| 01 | {{NAME}} | 1 | ⬜ not-started | — | — | — | — |

Legend: ⬜ not-started · 🔧 claimed · 🔎 built-awaiting-reconcile · ✅ closed-clean · ⚠️ closed-with-debt · 🚨 stale-claim

## Debt

Open items: {{N}} — see `debt.md`

## Detours

Open detours: {{N}} — see `detours.md`

## Blocked on Divya

<!-- EVERY item MUST end with "Recommendation: <one plain-English line>" —
     the dashboard renders it as a tinted box with a one-tap "Go with the
     recommendation" button (Divya's ask, 2026-07-09). An item without a
     recommendation forces her to compose an answer from scratch; that is a
     defect, not a style choice. Phrase the item itself as ONE plain question
     (jargon-free), context second, recommendation last. -->

- {{ITEM_OR_NONE — end with "Recommendation: <one line>"}}
