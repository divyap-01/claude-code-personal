---
name: debugging-protocol
description: Use when a bug, error, test failure, or "it doesn't work" report has more than one plausible cause, before starting work on any of them. Also use immediately after a fix attempt fails or the user says "still broken," when only user feedback can tell whether a fix landed, or when tempted to "just try the most likely fix first."
---

# Debugging Protocol (Differential Diagnosis)

## Overview

Serial guessing — fix the most likely cause, wait for the user to report "still broken," try the next — burns one full user round-trip per wrong guess plus all the thrown-away work. Six suspects can mean six feedback loops.

**Core principle: corner the cause BEFORE working on it. Fix work starts only when exactly one suspect is left standing.**

**REQUIRED BACKGROUND:** superpowers:systematic-debugging. This protocol governs how its Phase 1 ends and its Phase 3 begins whenever several causes are plausible. Its Iron Law still holds; this adds a second one.

**When to skip:** genuinely one plausible cause (you'd struggle to write a second suspect) → go straight to superpowers:systematic-debugging. If you CAN write a second suspect, the protocol is on.

## The Iron Law

```
NO FIX WORK WHILE TWO OR MORE SUSPECTS ARE ALIVE
```

"Most likely" is not "confirmed." Likelihood may order which evidence you gather first; it never licenses a fix.

## Board Detour Check (BLOCKING — run this every time, before step 1)

A bug in a module's territory is a **detour** from that module's plan — and if that module is run by the Conductor, the detour must be logged on its board or it's invisible to the owner (the Conductor cannot see your window; its board only knows what's written to its files). So every run of this protocol starts with one check: **does this bug belong to a module that has a Conductor board?**

1. **Check** `docs/superpowers/modules/*/` (in the main checkout — this project: `/Users/ddpda/Local/auntyskitchen/docs/superpowers/modules/`). Match the bug's area against each board's slug/keywords (a `blueprint.md` lists `sweep_keywords`). Decide, out loud: **covered by board `<slug>`**, or **no board covers this** (the "or not").
2. **If a board covers it → write an OPEN detour** into that module's `detours.md` (append a section; leave any existing prose/placeholder line). Use EXACTLY this shape (the local Conductor Dashboard parses `## Detour ` headings + `- **Field:** value` lines — get it wrong and it won't render):

   ```markdown
   ## Detour <next unused N, start at 1> — <today's date, YYYY-MM-DD>

   - **Plain story:** <1-2 sentences a non-technical owner reads on her dashboard: what went wrong in kitchen terms and where it stands — NO file paths, ids, or jargon>
   - **Still owed (plain):** <what remains, in the same plain kitchen language>
   - **What interrupted:** <the bug in one plain-language line>
   - **Phase affected:** <NN if it maps to a phase, else none>
   - **State at interruption:** <where the module's planned work stopped, or "none — standalone bug report">
   - **Resume bookmark:** <the exact next action — a diagnostic step now, the fix step once a survivor is declared, or where planned phase work resumes>
   - **Status:** open
   ```

   The two plain lines are MANDATORY (Divya's ask 2026-07-09 — her dashboard leads the detour card with them and tucks every technical field behind "full detail"; a detour without them renders as unreadable jargon on her screen). Keep them updated at the same moments you update the bookmark.
3. **Keep it current** as the protocol moves: update **Resume bookmark** when the survivor is declared (→ the fix step) and when you hand off. **Close it** the moment the bug is confirmed-fixed by evidence, OR the work hands to another session — set `- **Status:** returned <date>` (never leave a resolved detour `open`; an orphaned `open` detour nags on the board forever).
4. **If no board covers it →** say so in one line and continue; nothing to write.

**Safety rails:** touch ONLY that one `detours.md` (the board is a NAMED docs-only exception to "main checkout is read-only" — this file, nothing else in the main checkout). Never `git commit` in the main checkout. You are "the agent that got interrupted" writing your own detour — that is explicitly allowed; the scoreboard/other board files are NOT yours to edit.

## The Five Steps

1. **Write the suspect list (the differential).** Every plausible cause, numbered, BEFORE investigating any single one. For each suspect: the cheapest piece of evidence that would kill or confirm it. **Build the list with the scenario-mapping dimension sweep, not gut feel** — walk each dimension asking "could the cause live here?": *data* (the specific record/item involved, its shape, legacy dirt), *state* (first run vs re-run, mid-flight edits, stale caches), *people* (role, account, tenant/restaurant scoping), *environment* (staging vs production divergence, migrations applied to one DB, timing, scale). Intuition writes 3 suspects; the sweep writes 6 — and the missing 3 are tomorrow's "all suspects dead." Can't list suspects at all yet? That's an evidence problem, not a permission slip — do systematic-debugging Phase 1 (read the error, reproduce, check recent changes) until you can.

2. **Split the evidence by who holds it.** For each suspect, mark its killing evidence SELF (code reads, DB reads, logs, git diff, reproducing it yourself) or USER (facts that live in their world: what they clicked, which account, when it started, every time or sometimes). Never mark USER anything you could find out yourself.

3. **Fire the USER batch early, then investigate in parallel.** Send ONE batched question set (AskUserQuestion; >4 questions = consecutive calls, still one round) and gather your SELF evidence while you wait — the user's round-trip and your digging overlap instead of queueing. Design the batch as a decision tree: every question must kill at least one suspect *whichever way it's answered*. Observable, non-technical wording; multiple-choice with a recommended default. Needing a second round means the first was badly designed. Prefer the single observation that splits the whole field into buckets (e.g. "is the database right and only the screen stale, or is the database wrong?") over evidence that tests one suspect.

4. **Declare the survivor, out loud, before any fix.** State: "Cause: #4. Confirmed by: [evidence]. Killed: #1 because…, #2 because…" Two still alive → loop steps 2–3; never promote a favorite to fill the gap. **All dead → your list was incomplete**: return to step 1, re-run the dimension sweep for the dimension you skipped (the evidence you now hold usually names it), and log the miss per the Self-Improvement Loop below.

5. **Only now, fix.** Hand off to superpowers:systematic-debugging Phase 3–4: single hypothesis → failing test first → minimal fix → verify end-to-end. **The fix itself is ordinary coding work, so scenario-mapping fires on it as usual:** map every scenario the confirmed cause touches (every role, restaurant/tenant, data shape, and environment it can bite in) and make the fix cover the cause everywhere — not just the slice you reproduced. A half-covered fix comes back as "still broken," masquerades as a failed diagnosis, and restarts the loop this protocol exists to kill. Three scenarios that are ALWAYS in this map for multi-tenant, multi-environment systems: (a) verify in the environment the reporting user's screen actually hits, not just where the fix landed; (b) forward-only fixes (triggers, listeners, crons) leave a backlog from while the bug was live — plan the backfill; (c) **if the fix is a CHOKEPOINT fix ("guard the one front door every X passes through"), the chokepoint claim is a HYPOTHESIS — prove it by enumerating every caller of the underlying primitive** (`grep -rn "sendEmail(\|dispatch(\|write(" lib app`) and showing each one routes through the guard. Any caller that invokes the primitive directly is an UNGUARDED SIDE DOOR and the bug survives there. Enumerate; never assert. Evidence kills don't transfer across tenants either: a suspect killed with Kitchen A's rows is alive again for Kitchen B until re-killed.

## When a Fix Fails (the loop moment)

**First, separate wrong diagnosis from half-covered fix:** if the fix works in the scenario you verified but fails in another (different kitchen, role, item, environment), the survivor may still be correct and the fix under-scoped — that's a step-5 coverage miss, not a diagnosis miss. Both get logged (see Self-Improvement Loop), but they're patched differently.

Then: do NOT hop to the "next most likely" suspect. Return to step 1 and re-score the WHOLE list with the new information — a failed fix is itself evidence, and so is every new detail in the user's report (e.g. "it worked on Zahid's account" kills every affects-everyone suspect at a stroke). Add any new suspects the news implies. Each user report must shrink the field by *evidence*, never by crossing off the guess you just consumed.

## Special Entrances

- **The user names the cause** ("it's probably the cache — fix it"): their theory enters as prime suspect, first in line for evidence — but it still needs its confirming observation before fix work. Taking it on faith re-creates the guessing loop with their guess instead of yours.
- **The user can't be reached** (autonomous run, or you're a dispatched subagent): keep killing suspects with SELF evidence. If only USER answers can decide the survivors, deliver the narrowed field + the batched question set as your turn's output (or return it to your dispatcher) and stop there. Do NOT fix on a guess — a wrong "fixed it" costs more than a paused turn.
- **Evidence says two causes are BOTH real:** compound bug. Confirm and fix each separately (smallest first), re-verifying the symptom after each — per systematic-debugging, one change at a time.

## Question Quality Bar

| Bad (internal jargon) | Good (observable, splits the field) |
|---|---|
| "Is RLS blocking the update?" | "Does it fail for everyone, or only some people?" |
| "Did the mutation refetch the cache?" | "Right after it fails, refresh the page — does the number fix itself?" |
| "Which endpoint were you on?" | "Did this ever work, and roughly when did it stop?" |
| "Is the reconciliation logic wrong?" | "Was this the usual flow, or a variant — e.g. compared against an order/PO vs a plain scan? What's different about THIS one vs the ones that work?" |
| "Is it a unit-conversion bug?" | "On the two things being compared, are the units the same — e.g. is the order in dozens but the bill in single pieces?" |
| "Is her row draft-flagged / filtered out?" | "Did anyone ELSE hit this too, or only her?" — blast radius first; one-vs-many halves the field whichever way it lands |
| "Which code path handled the approval?" | "How exactly did it get resolved in the end — who did what, on which screen?" — the workaround's mechanism dates every after-the-fact observation (a badge/row/flag you see NOW may be aftermath of the workaround, not evidence of the cause) |

**For any COMPARE / RECONCILE feature (bill vs order, actual vs expected, A vs B), two discriminators are first-class and belong in round one:** (1) *which variant of the flow ran* — anchored-to-something (PO/order/baseline) vs a plain/standalone run; the "only difference this time" is usually the anchored variant. (2) *do the two sides share the same unit/UOM/basis* — a dozen-vs-piece / kg-vs-case / gross-vs-net mismatch makes every number look wrong at once.

**For any ONE-PERSON / ONE-RECORD report ("X couldn't…", "this item shows wrong…"), round one MUST include:** (1) *blast radius* — "only this person/record, or others too?" (2) *resolution mechanism* — "how did it eventually get resolved, exactly?" — without it you cannot tell post-incident evidence from workaround aftermath. (3) *fetch-now over recall* — ask the reporter to OPEN a screen during the round (timecard, pending-publish list, user list) rather than remember one from hours ago; recall returns "Not sure" exactly when it matters, and that's a wasted round.

## Red Flags — STOP, return to step 1

- "It's probably X, let me fix that" while other suspects sit unexamined
- A favorite suspect named before the field is narrowed to one
- Fix code exists before a survivor is declared
- A failed fix followed by grabbing the next suspect off the pile
- A second round of user questions the first round should have covered
- Deep-reading code only for the suspect you *hope* it is
- "Fixed" claimed after verifying only ONE tenant/kitchen/environment of a multi-tenant system
- You've handed the user a new theory *plus* a "try this" on two or more consecutive turns — that IS the serial-guess loop; the protocol should already be running
- You called a code line you found "the smoking gun" / "confirmed" without an observation showing it actually FIRES in the reported case
- You opened a PR / committed a fix while the differential still has ≥2 live suspects
- You confirmed a cause on data keyed to an id/token/name you never verified belongs to the exact thing the user is reporting on
- You called something a "one-off" / "rare" / "singleton" (or "recurring" / "widespread") from a flag/label/fingerprint count instead of measuring the phenomenon directly — a case inside a grace/threshold leaves no flag and hides from that count
- A suspect was killed with evidence about a DIFFERENT predicate than its firing condition — e.g. testimony "first punch of the day" (about punches happening today) accepted as a kill for "completed rows linked to this shift" (any date, any origin, including manual back-entries). Restate every suspect as its exact firing condition (the code's actual WHERE/IF) before accepting a kill; human answers describe events, guards read rows.
- Your recommended remedy MUTATES the state your confirming evidence reads (publish flips the draft flag, restart clears the log, resave rewrites the row) and you asked for the remedy first — evidence capture comes FIRST, remedy second, as an explicit numbered order in the message
- You gathered environment evidence (config dir, extension folder, version, settings file) for an install/profile you never tied to the user's LIVE process — on a machine with multiple installs/forks/profiles of the same tool, verify which one is actually running (`ps` + `--user-data-dir` / process tree) before any per-install fact counts as evidence; an unexplained second install is a live suspect, not a footnote
- You wrote (or are about to write) "this is the single chokepoint / front door / one place every X passes through" WITHOUT enumerating the callers of the primitive it guards — an architectural belief stated as fact. It repeats verbatim in the fix's commit message and the bug comes back months later through the side door nobody listed (2026-07-11: deactivated accounts kept getting commissary emails eight days after the "single front door" fix, because a second module called `sendEmail()` directly). Run the caller sweep; a chokepoint is proven, not declared.
- You presented a candidate list, example record, or "verify me with this" test drawn from the WHOLE system when the reporter only sees a filtered slice (their kitchen/tenant/role/visibility rules) — a full-catalog superset names records the reporter literally cannot reach ("Dahi is not even available for the Waterloo kitchen", 2026-07-10). Scope every candidate list and every user-facing example to the reporting user's actual visible surfaces BEFORE presenting; a superset is fine for private analysis, never for the user-facing answer
- You asked the user to perform a one-shot repro ACTION (a live save, click, or send you'll observe through logs/instrumentation) without first verifying the instrumentation is demonstrably recording — process alive AND fresh lines flowing, not merely started (`vercel logs` exits after one batch; a dead capture wasted the user's production save, 2026-07-11). Prove the harness captures live traffic BEFORE spending the user's action; a repeated ask is a second round

## Rationalizations — all mean STOP

| Excuse | Reality |
|---|---|
| "User is annoyed — grab the most plausible cause, patch it fast, pressure stops" | That instinct is what CREATES the failed-fix loop that makes them angrier. Pressure triggers this protocol; it never exempts it. |
| "The smoking gun in the code is obvious" | "Obvious" is what you said about the last wrong fix. Obvious ≠ confirmed — get the killing observation first. |
| "They said no back-and-forth, so I shouldn't ask questions" | ONE batched question set IS the minimum back-and-forth. Serial fixes are the real back-and-forth: feedback loop after feedback loop. |
| "The user already told me the cause" | They reported a symptom wearing a theory. Prime suspect, yes; verdict, no. |
| "I'll investigate my favorite while other checks run" | Read to KILL suspects, not to dress up a favorite. Discriminating evidence first. |
| "Only one cause is realistic here" | If you can write a second plausible suspect, the protocol is on. One-suspect bugs skip straight to systematic-debugging. |
| "The user is away, so I'll just fix the top suspect" | Deliver the question set and pause. An unconfirmed "fixed it" spends their trust, not just your time. |
| "The diagnosis was right, so the bounced fix isn't a protocol failure" | A half-covered fix restarts the exact loop this protocol kills. It trips the loop below the same as a wrong survivor. |
| "producer/dispatcher X is the single chokepoint — guarding it covers everything" | That's a claim about CALL-SITES, and call-sites are enumerable in 30 seconds. A module that calls the primitive (`sendEmail`, `insert`, `dispatch`) directly bypasses your guard entirely, and your fix ships with a false totality claim baked into its commit message. Grep the callers and show each routes through the guard — or the bug returns as "you said this was fixed." |
| "The code obviously contains this bug, so it's the cause" | A real bug you found by reading code is a live SUSPECT, not a verdict. A codebase holds many latent bugs that aren't THIS symptom. Confirm it actually FIRES in the reported scenario — and that it explains why the WORKING cases work — before naming it the survivor. |
| "It's a real bug regardless, so shipping its fix now is free" | Shipping a fix mid-diagnosis declares a survivor by action — to the user and to yourself. If it's not the cause, you've spent review, merge, and trust, and the loop restarts. Log the real bug, fix ONLY the confirmed survivor. |
| "I found the guilty code, I don't need to ask the user" | The code shows a cause is POSSIBLE; only an observation shows it's ACTUAL. If you're about to declare a survivor from code alone, you still owe the one question/observation that kills its rivals. |
| "I got the id/token from a screenshot or log, so it's the right record" | An identifier lifted from an old screenshot is not proof it's the record the user is reporting on now. In a multi-record system, verify the id/token/name belongs to the reported subject BEFORE trusting any data keyed on it — you can confirm a real cause on the wrong row and declare a wrong survivor. |
| "It's a one-off — only one record matches" | You counted a PROXY (a flag/label/fingerprint), not the phenomenon. A case within a grace/threshold often leaves NO flag, so flag-based counting silently undercounts. Before calling anything a one-off / rare / singleton, MEASURE it directly (e.g. clock-in minus scheduled start per shift), not via the derived label. |
| "The caveat covers me — I told them how to confirm" | A caveated declaration is still a declaration: the user hears "case closed", runs your remedy, and the evidence may be gone before the confirming read runs. Hold the field open until the read is back — and never sequence a state-mutating remedy ahead of the evidence that needs that state. |
| "The folder/config name matches the app, so it's the right install" | Name-matching is not process-matching. Machines carry multiple installs, forks, and profiles of the same tool with near-identical dir names (`~/.antigravity` vs `~/.antigravity-ide`). Evidence read from — or fixes written to — the wrong install look identical and silently do nothing. Tie the config dir to the LIVE process first; and if you stumble on a second install, reconcile which one the user runs before proceeding — don't file it as trivia. |

## Self-Improvement Loop (BLOCKING)

This skill maintains itself. A protocol failure that isn't captured WILL repeat; one that is captured cannot. This fires in the SAME session the failure is noticed — not "later."

**Tripwires — any of these means the PROTOCOL failed, not just the debugging:**

| Tripwire (observable event) | The miss |
|---|---|
| A declared survivor turned out to be wrong | Evidence was over-trusted — which observation lied, and why was it believed? |
| The real cause was never on any suspect list | Differential miss — which sweep dimension got skipped? |
| A second user question round was needed | Question-design miss — what should round one have asked? |
| The user volunteered the decisive clue unprompted | You never designed a question for the discriminating fact |
| A multi-cause bug got worked without this protocol firing | Trigger miss — the description/registration didn't catch it |
| The protocol only fired after the user told you to run it | Trigger miss — you served ≥2 turns of theory+"try this" without recognising the loop |
| A survivor was declared "confirmed" from code evidence alone, then fell | Over-trust of "possible" as "actual" — no firing observation was gathered |
| The fix bounced because it covered one scenario of a correct cause | Step-5 scenario-mapping was skipped or shallow |
| A bug was debugged in a module that has a Conductor board, but no detour was written (owner asks "why isn't this on the dashboard?") | Board Detour Check was skipped — the firefight went invisible to the board |

**On any tripwire, before the session ends:**

1. **Log it** in `failures.md` (same folder as this file): date, the bug in one line, which tripwire, what the protocol said vs. what actually happened, and any excuse used — verbatim.
2. **Patch this SKILL.md** so that exact miss can't repeat: a new rationalization row, red flag, question example, sweep dimension, or trigger keyword. Follow superpowers:writing-skills — the live failure IS the failing test (RED already ran, in production); for more than a purely additive row, verify the patch with a quick subagent re-run of the failure scenario.
3. **Close the entry with the patch it produced** — or an explicit "no change because…". An entry without a patch line, or an unlogged tripwire, is itself a protocol violation.

**Honesty clause:** this loop runs on discipline, not magic. It guarantees the SAME mistake never repeats — it does not promise new mistakes never happen. `failures.md` is the incident book; this file is the standard operating procedure it feeds.

## Real-World Impact

Serial guessing on an N-suspect bug: up to N user round-trips and N−1 discarded fixes. This protocol: one self-evidence pass + one question round (running in parallel) → one fix that lands the first time — and every miss makes the next run stricter.
