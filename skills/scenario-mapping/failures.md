# scenario-mapping — failure log (incident book)

Every mapping failure gets an entry, logged in the same session it's noticed (see "Self-Improvement Loop" in SKILL.md). Format per entry: **date • task • tripwire • what the map said vs what happened • patch produced.** An entry with no patch line is itself a violation.

---

## 2026-07-03 • LIVE (Divya) — iPad kiosk PWA: not full-screen, camera permission asked every time, one "No" bricked scanning • sweep miss (device & entry mode)
- **Tripwire:** bugs shipped in scenarios that were never on any table — the kiosk work never mapped installed-PWA vs browser behavior, the camera-permission ask/denied/ask-again states, or fresh-install vs long-lived-install differences (new Erin Mills install failed while the older Waterloo install worked).
- **What happened:** discovered live by Divya on a real iPad; a single denied permission prompt left the kiosk unusable with no recovery path, and the diagnosis session that followed also went off the rails (see debugging-protocol's failures.md, same date).
- **Patch produced:** new sweep dimensions "Device & entry mode" (permission prompts incl. denied/ask-again, installed vs browser, fresh vs long-lived install, offline) and "Time & history"; red flags for a missing device/install-mode row and for a permission prompt with no denied-state row.

## 2026-07-03 • baseline test of this skill (pre-upgrade), staged "Report a problem" button task • codification evidence, honestly labelled
- **Tripwire (partial):** none fired outright — the baseline agent produced a strong 33-row map. BUT it leaned on this project's CLAUDE.md rules and memories for the device rows, the saved-table location, and the evidence-based done gate; the skill text itself demanded none of those, so a copy running outside this project would lose them.
- **What happened:** good behavior was situational (environment-supplied), not enforced by the skill.
- **Patch produced:** the 2026-07-03 upgrade baked them in — device & time dimensions in the sweep, "lock the table to a repo file" in step 5, the row→proof completion gate in step 6, the question quality bar, the mini-map fast path, companion cross-references (gap-check, debugging-protocol, TDD), the mid-build trigger red flag, and this Self-Improvement Loop.

## 2026-07-03 • verification run of the upgraded skill (staged kiosk camera-denied + lost wifi-outage reports) • loop fired correctly, produced two adoptable gates
- **Tripwire:** none missed — this was the first live firing of this skill's own loop, during its verification test.
- **What happened:** the test agent logged the permission sweep miss AND an evidence-pending entry for the wifi row (correctly refusing to classify it before diagnosis), handed the multi-cause half to debugging-protocol, mapped the fix scenarios before any code, and drafted two rule patches.
- **Patch produced:** both adopted into SKILL.md — the Permission Gate (five mandatory rows for any OS-permission feature, incl. shared-device blast radius) and the Degraded-Path Sign-off rule (sign-off requires the real screen in the real condition + what the worker loses; prose is not sign-off).

## 2026-07-13 — Builder ran scenario-mapping AFTER building, not before
- Task: Stock Item modal shell reskin (ingredient-detail-modal.tsx)
- Tripwire: "A varying-data task got built with no table at all" — the dispatch brief explicitly said "Invoke scenario-mapping ... then build," but the Builder read the brief, went straight into code archaeology (reading the component, its 7 consumers), and only ran the Skill tool retroactively after the reskin was already committed.
- What happened in practice: the manual code-reading DID cover the same ground (all 5 modes, all 7 call sites) and the retroactive table came back with zero gaps — so no bug shipped. But that's luck, not process; a table run first could have surfaced the "wizardMode is dead code" and "Accounting tab has a pre-existing QBO 500" findings BEFORE writing any JSX, instead of as an afterthought.
- Excuse used: none stated explicitly, just skipped straight to "let me read the file" — closest rationalization-table match is "I already thought of the edge cases" (mentally mapped modes while reading code, never wrote the table until asked).
- Patch: none needed to the skill's content — the process is already correctly specified ("before ANY implementation code"). Logging this as a discipline miss for the agent, not a skill-content gap.
