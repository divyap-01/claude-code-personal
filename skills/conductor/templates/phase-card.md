---
phase: "{{NN}}"
name: "{{PHASE_NAME}}"
wave: {{W}}
status: "not-started"   # not-started | claimed | built-awaiting-reconcile | closed-clean | closed-with-debt | stale-claim
plan: "{{PATH_TO_docs/superpowers/plans_FILE or PENDING}}"
---

# Phase {{NN}} — {{PHASE_NAME}}

## Promises
<!-- Filled by the CONDUCTOR from the phase plan, before any claim. Each promise gets an ID.
     OPTIONAL: a promise MAY carry a nested checklist of sub-items (2-space indent) tracking
     what's done vs. left WITHIN it — the phase agent ticks these as work progresses, and the
     local Conductor Dashboard renders + toggles them (a promise shows "2/3 done"). Older
     phases without sub-items are unaffected; this is purely additive, never required
     retroactively, and the reconcile still judges the promise as a whole. -->

- [ ] **P1** — {{SPECIFIC_VERIFIABLE_PROMISE}}
  - [ ] {{SUB_STEP — optional}}
  - [ ] {{SUB_STEP — optional}}
- [ ] **P2** — {{SPECIFIC_VERIFIABLE_PROMISE}}

## Claim
<!-- Filled by the PHASE AGENT, first action after reading this card. -->

- Claimed by: {{SESSION_DESCRIPTION}} on {{DATE_TIME}}
- Worktree: {{.worktrees/PATH}}
- Branch: {{feat/BRANCH}}

## Build notes
<!-- PHASE AGENT only. Running notes: what landed, PR link, anything a reconciler or successor needs. -->

- {{NOTE}}

## Report card
<!-- Filled by the FRESH-EYES RECONCILER (never the builder). One row per promise. Every ✅ needs evidence.
     The last THREE columns are the plain-English layer the local Conductor Dashboard shows Divya
     (a non-technical reader). They are AUTHORED here, never auto-generated from the technical cells:
       - Plain verdict: EXACTLY one of  live-works | live-broke | built-untried | not-checked
         · live-works / live-broke require someone to have VERIFIED THE RESULT — watched the real
           thing actually happen. NEVER award live-works just because something is "in use" or
           "shipped"; usage is not verification (that is the exact trap this exists to prevent).
         · built-untried = code/existence-verified only, not walked live (the board's Level-2).
         · not-checked = unverified either way. Absent/blank/any-other-word → the dashboard shows
           "Not checked yet" (never a guessed badge).
       - Plain sentence: ONE kitchen-language sentence for a non-technical reader. NO file paths,
         code/table/column names, migration ids, PR numbers, test-file names, or the word
         "database" (say "stored information" / "behind-the-scenes update"). A live-works/live-broke
         sentence MUST say WHERE it was tried — the test copy (preview) vs the live restaurants (prod).
       - Confirmed: "yes" once the person who did the checking confirms the sentence is right; "draft"
         (or blank) while it's a first-pass summary — the dashboard shows a "draft" tag on drafts.
     Leave the three plain columns off entirely on an old-style card and the dashboard just shows
     "Not checked yet" — they are optional and additive. Do NOT put a raw "|" inside a plain
     sentence (it breaks the markdown table). -->

| Promise | Verdict | Evidence | Plain verdict | Plain sentence | Confirmed |
|---|---|---|---|---|---|
| P1 | {{✅ built / ⚠️ built-differently / ❌ missing}} | {{TEST_RUN / SCREENSHOT / WALKED_FLOW_LINK}} | {{live-works\|live-broke\|built-untried\|not-checked}} | {{one plain kitchen-language sentence — say test copy vs live}} | {{yes\|draft}} |

**Gaps resolution:** {{FIXED_BEFORE_CLOSE or DEBT_IDS_FILED or NONE}}

## At the pass
<!-- The after-build checklist the local Conductor Dashboard shows on the BACK of each ticket
     (flip the ticket → these are the "before it's served" checks). Authored by the reconciler when
     the phase is built. Each of the 7 standard checks is: done | owed | na  (owed = still to do;
     na = doesn't apply here). Default (line absent, or the whole section absent) → owed. NEVER mark
     a check done unless it genuinely happened — the dashboard trusts "done" as a real tick.
     Under any check you MAY add plain how-to detail so a non-technical reader (Divya) knows exactly
     what to do when she taps that check:
       - who:  "you" (Divya does it) or "an agent" (a dispatched agent does it)
       - do:   numbered steps in PLAIN kitchen language — real screens, real taps, no file paths /
               code names / migration ids / PR numbers / "database" (say "the app", "the update").
       - done: one sentence describing what "done" looks like (the observable result).
     Write the steps when you reconcile — you know what was built, so you know how to check it. Keep
     the 7 canonical labels EXACTLY as below (the dashboard's Mark-done matches on the label). -->

- Smoke test: {{done|owed|na}}
- Walked it live: {{done|owed|na}}
  - who: {{you|an agent}}
  - do:
    1. {{plain step — e.g. "Open the app on the Waterloo iPad, go to today's Closing checklist."}}
    2. {{plain step}}
  - done: {{what "done" looks like — the observable result}}
- Your sign-off: {{done|owed|na}}
- DB change live: {{done|owed|na}}
- E2E test: {{done|owed|na}}
- Support docs: {{done|owed|na}}
- Released: {{done|owed|na}}
