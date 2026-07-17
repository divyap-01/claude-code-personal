---
name: scenario-mapping
description: Use when starting any coding task whose input data or usage can vary — imports, parsers, bulk actions, matching, syncing, scheduling, screens used across devices or install modes (phone, tablet, kiosk, installed PWA), anything fed by real production data — BEFORE writing implementation code. Also before building the fix for a confirmed bug cause. Especially when the request sounds simple ("should be quick", "just add a button"), under deadline pressure, when the user says "don't ask questions", or when similar past work hit the fix-one-thing → test → another-thing-breaks loop.
---

# Scenario Mapping

## Overview

Bugs discovered one at a time during testing are scenarios that were never mapped. Listing a few edge cases from intuition is NOT mapping — intuition finds 5, a structured sweep finds 15, and the missing 10 become next week's live-session bugs. Map the full space first, ask everything at once, then code to the map.

**Violating the letter of this process is violating its spirit.**

**REQUIRED COMPANIONS:** gap-check (run alongside — every gap it finds becomes a row here), debugging-protocol (its confirmed cause defines the scenario space the FIX must cover), and superpowers:test-driven-development (each locked row becomes a failing test).

## When to use / When NOT to use

- Any feature or change fed by varying data or varied usage — **including bug fixes**: once debugging-protocol confirms the cause, map every scenario that cause touches (role, kitchen/tenant, device, environment, legacy data) so the fix lands everywhere, not just the reproduced slice. A half-covered fix comes back as "still broken."
- NOT for: copy tweaks, one-line flag flips, dead-code removal. If it's truly trivial, skip. If you're unsure, it's not trivial — map it.
- **Small task ≠ skip — use the mini-map:** a 3–6-row table takes 2 minutes. If every row is KNOWN, write one line — "Mapped: N rows, all KNOWN, no questions" — and proceed. The mini-map exists so this skill is never silently skipped as "overkill."

## The Process (in order, before ANY implementation code)

1. **Walk the real workflow.** Who triggers this, from where, holding what? List every entrance (button, deep link, retry, resume, notification tap, empty-state CTA).

2. **Sweep ALL dimensions — write a table, one row per scenario:**
   - **Data:** empty • missing/extra fields • malformed • duplicates • zero/negative numbers • huge • legacy-dirty • format variations you haven't seen yet
   - **State:** first run vs re-run • target already has data • mid-flight edit/cancel • concurrent users • stale caches
   - **People:** every role that can reach it • multi-restaurant/tenant • shared-device identity (who is "the user" on a kiosk?) • deactivated or boundary-case records
   - **Device & entry mode:** phone vs tablet vs desktop • installed PWA vs browser tab vs kiosk • OS permission prompts (camera, notifications, location) INCLUDING the denied and ask-again states — one "No" must never brick the flow • offline & flaky network • fresh install vs long-lived install
   - **Time & history:** records created BEFORE this feature existed (backfill?) • forward-only effects (triggers, listeners, crons) leaving a gap for events during an outage • timezone/DST • date boundaries
   - **Environment & scale:** staging vs production divergence • migrations applied to one DB but not the other • failure halfway (what's left half-done?) • 1 row vs 10,000

3. **Mark each row KNOWN (cite where the behavior is defined) or UNKNOWN.** A KNOWN cited from memory must be re-verified against the actual current code before build — a citation that doesn't survive contact gets promoted to a question, never silently decided.

4. **Ask every UNKNOWN in ONE batched message** — phone-prompt style: multiple-choice (AskUserQuestion where available; >4 questions = consecutive calls, still ONE round), a concrete example per question, 2–3 options, recommended default starred, so the user can answer "all defaults" in one word. If the user is unavailable or said "just build it": proceed on the recommended defaults and hand back that SAME single message as a confirm list. Never trickle questions across the session; never make a silent decision that isn't on the list. If building surfaces a brand-new fork, it comes back as an addendum to THIS message — not a drip of new questions.

5. **Lock the coverage table — and give it a home.** scenario → agreed behavior → where handled → the test that proves it. For anything bigger than a mini-map or spanning sessions, SAVE the locked table to a file in the repo (the feature's plan/spec doc) and link it from the PR — a table that lives only in chat evaporates exactly when the next session, agent, or reviewer needs it.

6. **Code to the map — and prove it at the end.** Each row pairs with a test (TDD for logic/API rows; a named manual device check for hardware/PWA rows). **Completion gate:** before claiming done, re-read the locked table and produce the row → evidence mapping (test name or observed check, per row). Any row without proof = NOT done — "the happy path works" is not evidence.

## Question Quality Bar

| Bad (abstract / jargon) | Good (concrete, decidable in one tap) |
|---|---|
| "How should we handle edge cases in the import?" | "A row has a price but no name — skip it, import it as 'Unnamed', or stop the whole file? (★ skip + show a count)" |
| "What about permissions?" | "A cook opens this screen — full view, read-only, or hidden? (★ hidden)" |
| "Should it work offline?" | "The kiosk loses wifi mid-count — block with a clear message, or save and sync later? (★ save and sync)" |

## Permission & Degraded-Path Gates (BLOCKING)

- **Permission gate:** if ANY row involves a capability behind an OS permission prompt (camera, photos, microphone, location, notifications), the table is INVALID until it contains all FIVE of these rows, each with its own agreed behavior and proof: (1) first ask, granted; (2) denied just now — what the user sees immediately (a silently dead control is never acceptable); (3) denied previously — the OS will NOT re-ask, so the blocked state must be visible BEFORE the tap, with recovery steps in plain language; (4) shared-device blast radius — on a kiosk/shared tablet one person's "No" binds every later user across shifts; the row names WHO can recover it and HOW, worded for whoever is standing at the device; (5) the primary job still completes with the capability blocked, if it's optional. Fewer than five = red-flag STOP, same as coding with no table.
- **Degraded-path sign-off:** a degraded-path row (offline, error, fallback) counts as "signed off" only when the sign-off showed the ACTUAL screen the worker sees in that state — evidenced on a real device in the real condition — plus one sentence naming what the worker LOSES ("the typed report is gone; they redo it"). A prose description ("shows an error, can retry") is not sign-off, and the row's proof column must cite the evidence.

## Rationalization table

| Excuse | Reality |
|---|---|
| "The user said don't ask questions" | That bans trickling, not the ONE batched round. A defaults-marked list answerable in one word IS minimal questions. |
| "I'll discover the edge cases while building/testing" | Discovery-by-testing finds them one at a time — exactly the slow loop this skill exists to kill. |
| "I already thought of the edge cases" | You listed intuition's top 5. Run the dimension sweep and write the table; the gap is the next live bug. |
| "I can't map until I see the real data/file" | The variations the data MIGHT have are themselves scenario rows. Map them now; each becomes a handled case or a question. |
| "Deadline — happy path now, harden later" | The map costs ~10 minutes. The fix-test-fix loop costs days, on live data, with the user watching. |
| "Too simple to need a map" | A simple task gets a mini-map in 2 minutes. Cost ≈ 0. |
| "It's a bug fix, not a feature — mapping doesn't apply" | The fix must cover every scenario the confirmed cause touches. Half-covered fixes come back as "still broken" and masquerade as failed diagnoses. |
| "It's the same screen, just on the phone/kiosk" | A second device or install mode is its own scenario column — permissions, offline behavior, identity, and layout all diverge (see gap-check's parity inventory). |
| "The table's in the chat, that's written down" | Chat evaporates at session end and compaction. Lock it to a repo file for anything multi-session. |
| "This row is obviously KNOWN" | Cited from memory ≠ verified. Re-check the citation against current code before build. |

## Red flags — STOP and go back to step 2

- About to write implementation code and no scenario table exists
- **Two or more turns of building or fix-shipping with no table — you're already inside the discover-by-testing loop; fire this skill NOW, not after the next bug**
- Asking the user a clarifying question for the SECOND time in one task
- A "default" was chosen that never appeared on any list the user saw
- Calling something an "edge case" that a real user does weekly
- Claiming done without the row → proof mapping (completion gate skipped)
- A device or install mode the feature will really run on (kiosk, installed PWA, phone) has no row in the table
- A permission prompt (camera, push, location) with no row for its denied / ask-again state

## Self-Improvement Loop (BLOCKING)

This skill maintains itself — same incident-book model as debugging-protocol. A mapping failure that isn't captured WILL repeat; one that is captured cannot. Fires in the SAME session the failure is noticed.

**Tripwires — any of these means the MAP failed, not just the code:**

| Tripwire (observable event) | The miss |
|---|---|
| A bug ships in a scenario that was never on the table | Sweep miss — which dimension was skipped? |
| The user says "actually there's a case you didn't list" | Sweep or workflow-walk miss |
| A second question round was needed | Question-design miss — round one lacked a concrete example or the right options |
| A varying-data task got built with no table at all | Trigger miss — invoked late or never |
| A locked row shipped with no test or evidence | Completion-gate miss |
| A row's agreed behavior turned out wrong in real use | The question hid the right answer — fix the example/options format |

**On any tripwire, before the session ends:**

1. **Log it** in `failures.md` (same folder as this file): date, the task in one line, which tripwire, what the map said vs. what actually happened, any excuse used — verbatim.
2. **Patch this SKILL.md** so that exact miss can't repeat: a new dimension bullet, question example, red flag, rationalization row, or trigger keyword. Follow superpowers:writing-skills — the live failure IS the failing test; for more than a purely additive row, verify the patch with a quick subagent re-run.
3. **Close the entry with the patch it produced** — or an explicit "no change because…". An unlogged tripwire is itself a violation.

**Honesty clause:** the loop guarantees the SAME miss never repeats — it does not promise new misses never happen. `failures.md` is the incident book; this file is the standard operating procedure it feeds.
