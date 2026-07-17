---
name: gap-check
description: Use when coding ANYTHING that lists, filters, hides, gates, or displays records — a flag/status/archive/visibility rule, a WHERE clause, a role gate, any list, dropdown, picker, search, schedule, or report — OR adding/moving any interactive control (button, toggle, link, drag handle, modal), ESPECIALLY an action whose correctness depends on the record's state (Approve, Submit, Send-back, Delete, Edit). Also when building a SECOND rendering of a screen (mobile face, redesign, compact/print/export view), showing a success confirmation backed by a background job (send, sync, notify, queue), or when anything runs on a schedule (cron, recurring checklist, weekly report, reminder). Also when a user reports "I can't see X / where did Y go", "I clicked X and nothing happened", "why was [action] available when the item wasn't ready", "it said sent but it never arrived", "the weekly/scheduled X never appeared", or a dashboard count that doesn't match its list. Run with scenario-mapping before claiming done.
---

# Gap Check

## Overview

The worst bug class in multi-screen apps: a record exists in the database, shows on screen A, and silently vanishes from screen B because of a hidden filter — and nothing on screen B says why. The user discovers it live, asks "why can't I see this person?", and someone has to search the entire codebase to answer. (Real incident: an employee visible on the Users list was invisible on the scheduler because of an availability flag no screen explained — cost a manual investigation.)

A sibling bug class lives one layer up, in the **controls**: a button, arrow, or toggle is right there on the screen but does nothing when used — covered by another element, wired to a no-op, or disabled with no reason given. The user clicks the obvious thing, gets no response and no explanation, and assumes the feature is broken. (Real incident: a date-picker's month arrows were unclickable because the month-name label was painted on top of them — clicks landed on the label, so changing months silently did nothing. Invisible in the code; obvious the second someone actually clicked it.)

And two cousin classes hide in TIME: a screen that says "Sent ✓" for something that never durably happened, and a scheduled thing that silently never ran. Lists show what exists — nothing shows what SHOULD exist but doesn't, unless you design that surface explicitly. (Real incident: a checklists audit found a weekend-monthly schedule that never fired — no screen anywhere showed the absence.)

**Core rule — no silent failure. (1)** A record may disappear from a screen, but never without a trace. **(2)** A control that looks usable must actually work — or visibly say why it can't. **(3)** An action must be defined for EVERY state the record can be in, and never offered in a state where it's wrong — no *Approve* on a check nobody did, no *Submit* on an empty form. **(4)** Whatever you build must follow the project's established design scheme — reuse the existing design system and never ship a one-off "style island." **(5)** When the same screen is rendered in a SECOND form, every field, column, and control on the source form must be accounted for on the new one — shown, deliberately relocated (discoverably), or explicitly dropped and signed off. **(6)** A success message must be TRUE — backed by the durable effect it implies, or worded honestly ("queued", "will send when online") with failures surfacing somewhere the user looks. **(7)** Something that was supposed to happen on a schedule and didn't must be noticeable from a screen — absence needs a surface too.

**REQUIRED COMPANIONS:** scenario-mapping — run it first; every gap found here becomes a row in its scenario table (and its Permission Gate covers controls deadened by OS permission denials). debugging-protocol — a live user report of a gap ("where did X go", "it never arrived") is usually a multi-cause bug: these nine gap classes seed its suspect list; diagnose there before fixing here.

## The nine gaps

1. **Cross-surface gap** — entity visible on surface A, missing on surface B, no on-screen explanation. **Includes aggregates:** a KPI card, badge, or tab-count that disagrees with the list it summarizes because it's computed with a different filter or a stale snapshot — two truths about the same number erode trust in both.
2. **Silent filter gap** — a query excludes records (flag, status, role, join, date range) and the UI shows no count, badge, or "N hidden because…" anywhere.
3. **Code–DB–UI drift gap** — a DB flag/status changes behavior but no screen displays it or edits it; or the UI implies a state the DB doesn't store.
4. **Dead-control gap** — a control that looks interactive (button, arrow, toggle, link, drag handle) does nothing when used: covered/obscured by another element (z-index, overlap, `pointer-events`), wired to a no-op / `href="#"` / empty handler, disabled with no reason given, or firing but producing no visible effect or feedback. Gaps 1–3 hide DATA without a trace; this one hides ACTION without a trace.
5. **State-behavior gap** — an action is offered (and works) in a record-state where it's meaningless, wrong, or destructive: *Approve* on a checklist nobody completed, *Submit* on an empty form, *Send-back* on something never started, *Refund* on an unpaid order, *Edit* on a locked record. The control isn't dead — it fires — but it should have been hidden or disabled for THIS state, or should do something different. (Real incident, 2026-06-18: a manager dashboard let you *Approve* a checklist that was never done — the Approve button rendered for every state because only "complete" was ever pictured.)
6. **Design-scheme gap** — what you built works and is visible, but it doesn't follow the project's established design system: off-palette colours, an ad-hoc component instead of the shared one, inconsistent spacing/typography/radii, a missing dark-mode pairing, or a style island that doesn't match the screens around it.
7. **Cross-face parity gap** — the same screen, report, or record is rendered in a SECOND form (a mobile face, a redesign replacing the old screen, a compact/"lite" view, a print/export/email version) and a field, column, status, or control present on the source form is silently absent from the new one. Each form looks complete on its own, so no single-screen check catches it. (Real incident, 2026-06-20: a mobile "second face" for cook screens can silently drop the desktop's price + tax column and still look finished.)
8. **Phantom-success gap** — the screen confirms an action succeeded ("Sent ✓", "Saved", a green toast) but the durable effect didn't — or might not — happen: success shown at enqueue time for a job that can fail, fire-and-forget sends whose failures go only to server logs, optimistic UI never reconciled, an offline "sent" that was actually lost. The inverse of gap 4: not a control that does nothing, a control that LIES about having done something. The user walks away trusting a checkmark; the failure surfaces days later as a no-show technician, an unsent reminder, a missing report — and nobody connects it back.
9. **Silent no-show gap** — something that was SUPPOSED to happen at a time didn't (cron, recurring checklist, weekly report, scheduled reminder, sync), and no surface shows the absence. Lists render what exists; NOTHING renders what should exist but doesn't — the absence of an expected record is invisible unless a screen is designed for it ("last ran", "next due", an overdue/missing badge, a gap-in-sequence marker). (Real incident: the checklists audit's weekend-monthly schedule that never fired — invisible for months.)

## The sweep (do in writing, before claiming done)

1. **List every surface** showing the entity you touched: pages, dropdowns/pickers, search, schedules, reports, exports, emails, kiosk. Grep the table name and API route; check every consumer — including ones your change didn't touch.
2. **List every filter** on those paths — the one you're adding AND every inherited one (flags, status checks, role gates, joins that drop rows, default date ranges).
3. **For each filter × surface, answer:**
   - Where does the user SEE that filtering happened? (badge, "N hidden — show" link, empty-state text naming the reason, "(archived)" tag)
   - Where can the user CHANGE the underlying state? (a labeled control on a findable screen — a DB column alone doesn't count)
   - If excluded here, on which screen IS the record still visible? (must be somewhere)
   - **Count consistency:** any count shown anywhere (KPI card, tab badge, sidebar number) must be computed from the SAME filter as the list it summarizes — or visibly label what it counts. A card saying 3 above a list showing 5 is a gap.
4. **Search rule:** a search/picker that finds zero results for a record that EXISTS but is filtered must say so — "1 archived match — show it?" — never plain "No results".
5. **DB flag audit:** list every behavior-changing flag/status column on the entity (existing + new). Each must have a screen that displays it and a screen that edits it. Checking the schema to reuse a column is NOT this audit — you're hunting for invisible flags, not free columns.
6. **The missing-person test (acceptance bar):** if the user asks "why can't I see X here?", can they answer it themselves from that screen in under 10 seconds? If the answer lives only in the code, it's a gap.
7. **Exercise every interactive control you added or moved — actually use it, do NOT eyeball the JSX.** This step is hands-on, not on paper: overlap / z-index / `pointer-events` bugs are invisible in the code and only show at runtime. For each new or moved button, arrow, toggle, link, or drag handle:
   - **Click it for real** — in the running app or a click-test (Playwright). "The handler is wired" is not verified until a real click reaches it. A click-test that *times out clicking a visible control* is a finding, not a flaky selector — suspect something on top of it.
   - **Confirm the click LANDS on the control.** If a click does nothing, check what element is actually on top at the control's centre: `document.elementFromPoint(cx, cy)`.
   - **Confirm a VISIBLE effect.** The screen changes the way the user expects — an affordance whose effect isn't visible is a misleading affordance, worse than none.
   - **If it's intentionally disabled or inert right now**, the screen must say why (tooltip, helper text, greyed-with-reason). A silently-dead control reads as "broken," not "not yet."
   - **Scope rule (2026-07-04):** "no new/moved controls" NEVER exempts this step when the change redefines what an existing control MEANS (a filter that now slices numbers, a toggle that now gates more) — every entrance to the changed behavior is in scope, on every device width. And a click that produces SOME effect (panel closes) but not the control's INTENDED effect (state unchanged) is a dead control with a costume, not a working one.
   - **The dead-control test (acceptance bar):** if the user clicks the obvious control and nothing happens, does the screen tell them why within one try? If not, it's a gap.
8. **Build the state × action matrix — for every action on a record that can be in more than one state.** Do this in writing, BEFORE coding:
   - **List every STATE the record can be in — not just the happy one.** The state you forget to list is the one that ships broken.
   - **List every ACTION/affordance on it** — Approve, Send back, Submit, Edit, Delete, Reopen…
   - **Fill EVERY cell (state × action) with the required result:** available & does X / hidden / disabled-with-a-visible-reason. A blank cell = "didn't think about that state" = the bug.
   - **Gate the control on state — never render it unconditionally.**
   - **Reuse the ONE state source** (the status helper / enum the rest of the app already uses) so the control's idea of "complete" can't drift from what the list shows.
9. **Design-scheme check — does it match the rest of the product?**
   - **Read the project's design source of truth FIRST** (DESIGN.md / PRODUCT.md / tokens file) — never design from memory.
   - **Reuse** the existing shared components, tokens, colours, spacing scale, typography, radii, shadows and interaction states.
   - **Pair every light-mode style with its dark-mode equivalent** (if the product themes).
   - **Put it next to the neighbouring UI and check it belongs** — not a style island.
   - Empty / loading / error states follow the system too, not just the happy state.
10. **Parity inventory — when a screen is rendered in a second form, or a new form replaces an old one. A literal count sheet, source → new:**
   - **Inventory the SOURCE form:** every field, column, label, status, badge, and interactive control — per record AND at page level.
   - **Account for EVERY source item in exactly one bucket:** (a) present; (b) relocated / progressively disclosed, with the move itself discoverable; (c) deliberately dropped — named out loud and signed off, never silent.
   - **Reuse the source form's data and action wiring** — the new face calls the SAME handlers and queries; a re-implemented control is where "looks identical, behaves differently" creeps in.
   - **Put the two forms side by side, tick the inventory off item by item, and click every control on the NEW form.**
   - **The parity test (acceptance bar):** every source element is pointable-to on the new form — or to the explicit decision that moved or dropped it.
11. **Success-claims audit — for every success confirmation your change shows (toast, checkmark, "sent/saved" status):**
   - Name the DURABLE effect backing it. If the confirmation fires at enqueue/optimistic time, the wording must say so ("Queued", "Sending…") — ✓ means done, and users plan their day around it.
   - Name where a downstream failure SURFACES for the user (a failed badge with retry, a status line on the record — "logged server-side" does not count; users don't read server logs).
   - If the action can happen offline/flaky, name what the user sees when it didn't actually go through — an unmissable NOT-SENT state that preserves their work, never a green lie.
12. **Expected-producer audit — for every time- or event-driven producer you touched (cron, trigger, scheduled email, recurring checklist, sync, report generator):**
   - Where does a user SEE that it ran? (the generated item, a "last ran / as of \<time\>" stamp)
   - How would a user NOTICE it DIDN'T run? (an overdue/missing badge, a visible gap in a dated sequence, a "hasn't run since…" warning) — if the honest answer is "they wouldn't," that's a gap 9.
   - Who is told when it fails, on which screen?

## Resolving gaps

- **Fixable in scope** → fix it (an empty-state line, honest toast copy, or a "last ran" stamp is usually one line of UI).
- **Product judgment** (hide vs grey-out vs badge vs reveal-toggle) → ask, batched per scenario-mapping, WITH a recommendation. Default: show a count/hint with a one-tap reveal. Never recommend silent hiding.
- **Out of scope** → name it as a tradeoff ("this ships with X invisible on Y and no hint — OK?"). Never silently leave it.

## Rationalization table

| Excuse | Reality |
|---|---|
| "They disappear from every dropdown automatically — that's the feature" | Disappearing is the feature. Disappearing WITHOUT A TRACE is the bug. Each surface needs its hint. |
| "The management page has the Show-hidden toggle" | The user isn't on the management page when they hit the gap — they're staring at a picker missing a name. |
| "Adding hidden-counts everywhere is clutter/scope creep" | One line of empty-state text is the cheapest support ticket you'll ever prevent. |
| "I checked the schema before adding the column" | Reuse-checking ≠ flag audit. The question is which EXISTING flags already change behavior with no UI. |
| "Search just won't return archived items" | A user searching an exact name and getting 'No results' for a record that exists WILL file a bug. Say "1 archived match". |
| "I only changed one screen" | The flag filters every consumer of that table. Sweep them all — especially the ones you didn't touch. |
| "The handler's right there in the code — it's wired" | Wired ≠ clickable. A label or overlay painted on top eats the click while the code looks perfect. Click it for real. |
| "It worked when I looked at it / in the happy path" | Overlap bugs depend on layout, width, and stacking order. Click it in the running app at the real size — not in your head. |
| "My click-test timed out — probably a selector quirk" | A click that won't land is often the bug itself. Check what's covering the control BEFORE blaming the test. |
| "The button's just disabled / not wired yet" | A silently-inert control reads as broken. "Disabled" needs a visible reason on the same screen. |
| "The Approve/Submit button is generic — it works the same everywhere" | Its availability and meaning depend on the record's state. Build the state × action matrix. |
| "I built the complete / happy state" | The other states still render the same control. Every state shows it unless you gate it — write what each cell does. |
| "No state is missing, I'm pretty sure" | Don't guess — list them. The missed / empty / not-started / already-actioned states are exactly the ones that ship broken. |
| "It works — the styling is close enough" | Off-scheme UI reads as unfinished and untrustworthy. Match the design system or it's a gap. |
| "I'll match the design later / I styled it from memory" | Designing from memory is how style islands happen. Read the design source of truth FIRST. |
| "The mobile/new version has everything important" | "Important" is the trap — list every element and account for each. The one you judged unimportant is the one the user came for. |
| "I rebuilt the screen, it's basically the same" | "Basically" is not a count. Inventory element-by-element and tick each off. |
| "The new view is simpler on purpose" | Simpler-on-purpose is bucket (c): name what's dropped and get it signed off. Simpler-by-accident is the parity gap. |
| "The toast just confirms the request was accepted" | The user reads ✓ as DONE and plans around it. Confirmation at enqueue time must say "queued" — and the failure must have a screen. |
| "Failures are logged server-side" | Users don't read server logs. A failure that surfaces nowhere the user looks is a phantom success. |
| "The cron ran fine in every test" | The gap isn't the cron failing — it's that NOBODY WOULD NOTICE if it did. Absence needs a surface: last-ran stamp, overdue badge, gap marker. |
| "The KPI is only slightly stale / off by one sometimes" | Two disagreeing numbers about the same thing erode trust in both. Same filter, same source — or label the difference. |

## Red flags — STOP

- A screen that FLAGS a problem/error (mismatch, "off by", "N flagged") but offers no control to FIX it — only "accept anyway" / "dismiss" or editing an unrelated field. A dead-end error is top-severity; rank ACTIONABILITY (can the user resolve the flag right here?) ABOVE visibility (is the label shown?). Don't let "add the missing label" headline a plan while the user still can't act on what's flagged.
- A gap-check that ran CODE-READ ONLY (no running app) and did not SAY SO — code-reading systematically under-weights inert controls; when step 7's hands-on click-test can't run, flag that limit and make "for every error/flagged state, what can the user DO about it here?" the #1 question.
- You added/changed a WHERE clause or flag and zero UI text changed anywhere
- An empty state that says only "No results" on a filtered list or picker
- A behavior-changing DB column with no screen that shows it
- You can't name, for an excluded record, the screen where it's still visible
- The phrase "hidden automatically" in your own plan with no per-surface hint next to it
- A new or moved interactive control you never actually clicked in a running app (only read the code)
- A click-test that times out clicking a *visible* control — suspect an overlay/stacking issue, not the test
- An absolutely-positioned control added near other painted elements with no z-index discipline
- A button or link whose handler is empty, `href="#"`, or a no-op stub
- "I clicked it and nothing happened" with no on-screen feedback (loading, error, or state change)
- An action button (Approve / Submit / Send-back / Delete) rendered with NO condition on the record's state
- You designed only the "complete / happy" state and never wrote what each control does for the rest
- A new screen / component / control that doesn't visibly match the design system, or UI built without reading the design source of truth first
- A screen rendered in a second form with no element-by-element source→new inventory written down
- A control re-implemented for the new form instead of calling the source form's existing handler
- "Basically the same" or "has everything important" standing in for an actual element count
- A success toast/checkmark shown at enqueue time (or optimistically) with no reconciliation and no visible failure path
- A fire-and-forget job (email, notification, sync) whose failure surfaces only in server logs
- A cron / scheduled producer with no user-visible "last ran / next due" and no way to notice a missed run
- A KPI, badge, or tab-count computed with a different filter (or a stale snapshot) than the list it sits beside
- A sweep pass that found ZERO gaps on a change touching three or more surfaces — suspect the sweep, not the code

## Self-Improvement Loop (BLOCKING)

This skill maintains itself — same incident-book model as debugging-protocol and scenario-mapping. A gap class or sweep step that misses in real life gets patched the day it misses.

**Tripwires — any of these means the CHECK failed, not just the code:**

| Tripwire (observable event) | The miss |
|---|---|
| A user discovers a gap live after the sweep passed | Which sweep step should have caught it — or is a gap CLASS missing? |
| A gap is found that fits NO existing class (you had to stretch a definition) | A missing class — name it and add it; stretched classes get demoted severity and unreliable catches |
| "I clicked X and nothing happened" on a control you click-tested | The test environment diverged from real use (size, device, data) — tighten step 7's conditions |
| A second form shipped without a parity inventory | Process miss — the trigger for step 10 didn't fire |
| A sweep found zero gaps on a multi-surface change and a gap later surfaced | The sweep was shallow — record which step was rushed |
| This skill never fired on qualifying work | Trigger miss — the description/registration didn't catch it |

**On any tripwire, before the session ends:** (1) log it in `failures.md` (same folder): date, the feature, which tripwire, what the sweep said vs. what happened, any excuse verbatim; (2) patch this SKILL.md so that exact miss can't repeat (new class, sweep line, red flag, or rationalization row); (3) close the entry with the patch produced — or an explicit "no change because…". An unlogged tripwire is itself a violation.

**Honesty clause:** the loop guarantees the SAME miss never repeats — it does not promise new misses never happen. `failures.md` is the incident book; this file is the standard operating procedure it feeds.
