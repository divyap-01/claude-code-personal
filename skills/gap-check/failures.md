# gap-check — failure log (incident book)

Every check failure gets an entry, logged in the same session it's noticed (see "Self-Improvement Loop" in SKILL.md). Format per entry: **date • feature • tripwire • what the sweep said vs what happened • patch produced.** An entry with no patch line is itself a violation.

---

## Pre-log incidents (the skill's founding wounds, already narrated in SKILL.md)
- Employee visible on Users list, invisible on the scheduler, no explanation anywhere → gaps 1–3 + the missing-person test.
- Date-picker month arrows unclickable under a painted label → gap 4 + the hands-on click rule (step 7).
- 2026-06-18: *Approve* offered on a checklist nobody completed → gap 5 + the state × action matrix (step 8).
- 2026-06-20: mobile second-face nearly dropping desktop columns unnoticed → gap 7 + the parity inventory (step 10).

## 2026-07-03 • checklists audit finding: weekend-monthly schedule NEVER fired, invisible for months • gap class missing (silent no-show)
- **Tripwire:** a gap was found (in a whole-module audit) that fit no existing class — lists show what exists; nothing showed the absence of the runs that should have existed.
- **What happened:** the sweep had no step asking "how would a user notice a scheduled thing DIDN'T happen?" — absence had no surface, so the miss was undetectable from any screen.
- **Patch produced:** gap 9 (silent no-show), sweep step 12 (expected-producer audit), red flag for producers with no "last ran / next due", rationalization row "the cron ran fine in every test."

## 2026-07-03 • baseline test (pre-upgrade), staged Equipment Maintenance module • classes caught only by stretching
- **Tripwire:** gaps found that fit no class — the fire-and-forget "Reminder sent ✓" toast was filed under *dead control* (it's the inverse: a control that LIES about succeeding), and the untraceable cron was caught but demoted to "lower severity" precisely because no class named it.
- **What happened:** a careful agent caught them by stretching definitions; a rushed session or weaker reviewer would not. Unnamed classes get caught by heroics, not by rule. The staged KPI-vs-list disagreement (status column refreshed nightly vs live date filter) also had no explicit home.
- **Patch produced:** gap 8 (phantom success) + sweep step 11 (success-claims audit); gap 9 formalized (see entry above); count-consistency added to gap 1 and sweep step 3; new red flags (enqueue-time ✓, fire-and-forget jobs, stale KPI, zero-findings-on-multi-surface-change); Self-Improvement Loop + this incident book added; debugging-protocol cross-reference (live gap reports are multi-cause bugs).

## 2026-07-04 • Timesheets role-filter slice • dead phone checkbox observed, excused as "viewport"
- **Tripwire:** a control that died in real use after my own hands-on pass touched it — I tapped a role checkbox in the phone Filters sheet, the panel closed with NOTHING applied (nested-popover outside-click), and I wrote it off as "narrow layout quirk, I'll test on desktop" instead of logging a dead-control finding. The U3 cold agent reproduced it 3× and called it a BLOCKER: the phone had NO working way to filter by role.
- **What happened:** my gap-check pass had declared "no new/moved controls" — technically true, but the change made the ROLE FILTER the headline job, which promotes every entrance to that filter (incl. the pre-existing phone sheet) into scope. Root causes were two stacked layout bugs: a Popover nested inside the Filters Popover (inner tap = outer outside-click) AND the sheet overflowing the viewport (post-fix retest click timed out at y≈892 in an 844px viewport — this time treated as the bug per the skill, elementFromPoint → off-screen).
- **Patch produced:** SKILL.md control-layer rule extended: (a) "no new controls" NEVER exempts the hands-on pass when a change redefines what an existing control MEANS — every entrance to the changed behavior is in scope on every device width; (b) "the click did something (closed the panel)" is not "the click WORKED" — the visible effect must be the control's INTENDED effect (a panel closing while the state stays unchanged is a dead control with a costume).

## 2026-07-08 • LIVE (Divya) receive "Decadently Yours" against a PO • dead-end flagged items — sweep found it but SYNTHESIS mis-ranked it under cosmetics
- **Tripwire:** user hit a gap live after the sweep "passed" — 10 flagged lines with NO action available (only the received-qty number editable; "Accept anyway" swallows the variance; NO pack/unit-size control on a matched line). Divya: "I don't see anything in the gap check report saying there are things on the UI missing from what the code is doing... no way I can change the pack size."
- **What happened:** the sweep DID find the dead-control gap (matched lines can't re-pick a pack — the picker is gated to unmatched/awaiting lines) and listed it. But the SYNTHESIS led with class-3 "show the unit label next to Billed" (visibility) and ranked the actionability dead-end below it. The lived blocker isn't "the label is missing" — it's "the screen names an error I have NO control to fix." Compounded by: this sweep was CODE-READ ONLY (no running app this session), so sweep step 7's hands-on click-test never ran — the lived severity of an inert control is exactly what code-reading under-weights.
- **Excuse (mine, implicit):** presented "add unit labels" as the headline Wave-1 fix; treated "no way to fix the flag" as a secondary dead-control item.
- **Patch produced:** new red flag ("a screen that FLAGS a problem but offers no control to FIX it — only 'accept'/'dismiss' or editing a different field — is a top-severity dead-end; rank actionability ABOVE visibility"); new rationalization row; sweep step 7 note: when the hands-on click-test can't run (no running app), SAY SO in the report and rank "for every error/flagged state, what can the user DO about it right here?" as the #1 question, since code-reading systematically under-weights inert controls.

## 2026-07-09 — Conductor dashboard: user found 2 control gaps AFTER my sweep passed
- **Feature:** Conductor dashboard live-update debug → redesign (standalone local tool).
- **Tripwire:** "A user discovers a gap live after the sweep passed" — TWICE in one session. (1) Ticket status pill is a BUTTON that cycles/writes status on tap (class-5 state-behavior: an edit affordance where only display belongs). (2) Per-ticket "Works / Has an issue" buttons only append a note to divya-notes.md; no visible state changes anywhere (class-8 phantom action + Gate-5 invisible effect).
- **What the sweep said:** I reported 3 findings (grey badges, data-changes jargon strip, constant "7 owed") and moved on to fixing. I never ran step 7 (hands-on click every control) on the existing dashboard, and did not SAY the control layer was unswept — the exact "code-read-only and didn't say so" red flag.
- **Excuse used (verbatim, internal):** treated the sweep as done because the user's original complaint (live updates) was answered; controls felt out of scope for a "data freshness" bug.
- **Patch:** no new class needed — classes 5/8 and step 7 already cover both misses; the failure was scope-shrinking the sweep to the reported symptom. Enforcement line added to my working memory (feedback memory: run the FULL control sweep on any surface I'm about to modify/redesign, before the user tests it), and this entry is the record. Also: the user's explicit working rule — she should never be the one finding the gaps; praising her finds instead of preventing them is the anti-pattern.

## 2026-07-09 (night) — By-PR view: check chips dead on every card except the first
- **Tripwire:** "I clicked X and nothing happened" on a control I click-tested. The same card's Before-it's-Live strip renders on SEVERAL PR cards; panel ids were phase+index only, so every copy shared ids and getElementById opened the FIRST copy (inside a different card) — taps on later copies looked dead. My click-test had tapped only the first instance.
- **Patch (lesson):** when one component renders MULTIPLE TIMES on a surface, the hands-on click-test must exercise a NON-FIRST instance — duplicate-id deadness is invisible on instance #1 by construction. Fix shipped: per-context id suffix.

## 2026-07-10 — HQ product fixes claimed "fixed/merged" without the control sweep or the phone face
- **Tripwires (two, both owner-caught live):** (1) HQ B1 "Duplicate broken → FIXED, merged #2273" — but on the real screen the ⋯ menu has NO Duplicate option at all (Edit/Rename/Retire/Remove only). A claimed-fixed control that doesn't EXIST on the live surface = the hands-on click of the actual control was never done post-merge. (2) HQ B4 "phone buttons small" — reality: HQ Recipes is INVISIBLE on the phone; the whole HQ module shipped desktop-only despite the standing "both faces together" rule (cross-face parity, class 7).
- **The miss:** product-side agents (and the reconciler that accepted "MERGED→dev" as fixed) never ran the gap-check step-7 click on the real merged surface, and never opened the phone face at all. The board then relayed the false "fixed — awaiting click-through" to the owner, who burned her checking time discovering controls that don't exist.
- **Patch:** conductor SKILL now requires reconciliation to accept a bug as "fixed" ONLY with click-on-the-real-merged-surface evidence (and the phone face wherever the kitchen product has one). Board record: B1/B4 reopened with her evidence; systemic B8 filed (HQ has no phone face).
