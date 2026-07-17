---
name: conductor
description: Use when a whole module or project needs end-to-end delivery — idea → module blueprint → phased waves → execution → reconciliation → honest close — or when adopting an existing half-built module to get a verified scoreboard of what's done, half-done, and owed. Triggered by /conductor <new|adopt|run|dispatch|status|close|housekeeping> <module>, or by asks like "plan this whole module start to finish", "where are we REALLY on X", "what's still owed on X", "run the next phase", "give me prompts for the next wave", "clean up stale worktrees/branches".
---

# The Conductor — end-to-end module delivery

## Overview

The Conductor takes a module from idea to *actually finished*. It contributes exactly two inventions — the **Module Blueprint** (full-module ideation, not slice-sized) and the **Module Board** (a persistent job board in the repo) — and otherwise composes the existing skill library. It never re-implements an installed skill (advisor's rule: a hand-written parallel copy forfeits every patch the real skill carries).

**Core principle: the plan stays the boss.** No build without a board. No phase closed without a fresh-eyes report card. No skip without a signed debt entry. No firefight without a resume bookmark.

**Honest limits (say them, don't hide them):** the Conductor cannot steer other live agent windows — it steers via the prompts it mints and the sweep it runs when work lands. Human items (Divya's device smoke tests, sign-offs, merges to main, production migrations) are tracked and nagged, never performed autonomously.

## The Board

Path: `<main checkout>/docs/superpowers/modules/<module-slug>/` (this project: `/Users/ddpda/Local/auntyskitchen/docs/superpowers/modules/<slug>/`).

| File | Contents | Writer |
|---|---|---|
| `blueprint.md` | Job sentence, scope, "finished means", phase/wave table with dependencies | Conductor only, after Divya approves |
| `scoreboard.md` | Phase status table, `stale_hours`, `current_wave`, last-verified stamp | Conductor ONLY — single writer |
| `phases/phase-NN-<slug>.md` | Promises, claim, build notes, report card | Skeleton+promises: Conductor. Claim+build notes: that phase's agent ONLY. Report card: the reconciler ONLY |
| `debt.md` | Every confessed skip + Divya's sign-off (owed PROCESS items) | Conductor only |
| `bugs.md` | Bug register: built-but-not-working-right defects found in real use; closes only on verified-fixed evidence (live re-walk), never a merged PR alone | Conductor only |
| `detours.md` | Interruptions + resume bookmarks | Conductor, or the interrupted agent |

**Why the main checkout:** builds are worktree-isolated, so a card inside an unmerged branch is invisible to everyone else. The board is the one wall every window can see. This is a NAMED, NARROW exception to "main checkout is read-only": it covers ONLY `docs/superpowers/modules/**`, docs-only, each actor touching only its assigned files. Code changes in the main checkout remain forbidden.

**Commit rhythm (snapshot — NEVER `git add/commit` in the main checkout):** the live board is working files in the main checkout (untracked is normal for docs here). At natural points (board creation, wave unlock, phase close, debt sign-off) the Conductor snapshots it: ensure the worktree `.worktrees/module-boards` on branch `chore/module-boards` exists (create once off `origin/dev`), copy the module's board folder in, commit there, push. The snapshot branch is PR'd into `dev` at module close. Between snapshots the working files ARE the live board; if an edit is lost, the reality sweep + latest snapshot rebuild it — the board is self-healing.

**Statuses:** ⬜ `not-started` · 🔧 `claimed` · 🔎 `built-awaiting-reconcile` · ✅ `closed-clean` · ⚠️ `closed-with-debt` · 🚨 `stale-claim`.

Templates for all five files: `templates/` next to this skill. Copy verbatim, fill every `{{TOKEN}}`. Instance naming: `templates/phase-card.md` → `phases/phase-NN-<phase-slug>.md` (NN = blueprint phase number, slug = kebab-cased phase name). While a phase is in flight, the scoreboard is authoritative; a card's front-matter `status` is the agent's signal, folded into the scoreboard by the next Conductor sweep.

**Blocked-on-Divya items always carry a recommendation (BLOCKING, Divya's ask 2026-07-09).** Every item written to a scoreboard's "## Blocked on Divya" list MUST be ONE plain-English question (no jargon) ending with `Recommendation: <one line>`. Her dashboard renders that as a tinted recommendation box with a one-tap "Go with the recommendation" button — an item without one forces her to compose an answer from scratch and is a defect. When sweeping existing boards, retrofit recommendations onto any bare items you touch.

**Dashboard coordinates may only point at existing CARD files (BLOCKING, learned 2026-07-11).** The dashboard renders `phases/*.md` card files ONLY — a scoreboard-row annotation with no card is invisible to Divya. Before citing any "on your dashboard" coordinate, verify the card file exists; if a phase Divya must see has no card yet (plan unwritten), mint a skeleton card first — promises `P-PENDING` plus the already-decided facts in plain language. (2026-07-11: HQ 19/22/23 were annotated scoreboard-only and cited as coordinates; she could see none of them.)

**Every report to Divya ends with dashboard coordinates — in NAMES, not numbers (BLOCKING; Divya's ask 2026-07-09, names-first corrected 2026-07-11).** When any agent tells her about module work — in chat, a handover, a PR description — the report's last line points at her dashboard in the vocabulary HER SCREEN shows: `On your dashboard: <Board> → the "<card NAME>" card → the "<promise's plain words / check name>" promise — <what changed on screen>`. Her board deliberately hides card numbers, promise P-ids, PR numbers, and bug tags (the 2026-07-11 calm-board slice; "Show team codes" is off by default) — so "card 19 → P6" points at NOTHING she can see. Names are the coordinates; numbers/PR ids may ride in a trailing "(for the team: card 19 P6, #2442)" parenthetical only. She could not relate chat narratives to the board without coordinates (2026-07-09), and could not follow number-coordinates at all (2026-07-11). Do NOT "fix" this by re-showing codes on her dashboard — she explicitly rejected that (an unasked change was made and reverted same day); fix the language, never her tool.

**A bug is "fixed" only with click-evidence from the real merged surface (BLOCKING, learned 2026-07-10).** Reconciliation may NOT accept "fixed — MERGED→dev" on a bugs.md row unless the fixer (or reconciler) evidences the gap-check step-7 click on the ACTUAL surface post-merge — the exact control, the exact screen — and, for any user-facing surface, the PHONE face too (the kitchen product is two-faced; HQ shipped desktop-only and its "fixed" Duplicate control didn't even exist on the live menu — both owner-caught 2026-07-10, see gap-check failures.md). "The PR merged" is delivery, not repair.

**Every check aimed at Divya names its exact PLACE (BLOCKING, learned 2026-07-10).** A "sanity check owed:" / who-you check that doesn't say WHERE to stand is unusable — she hit three in one sitting ("how to duplicate, where, which kitchen?"). Every such instruction names: the FACE (Headquarters vs a kitchen vs the phone), the screen path (HQ → Recipes), the tap sequence, and what "done" looks like. "Duplicate a recipe" is a defect; "at HEADQUARTERS → Recipes → ⋯ menu on any recipe row → Duplicate; done = a full copy appears" is the standard.

**Every bug repair needs a named sanity test before it counts as fixed (BLOCKING, Divya's ask 2026-07-09).** A bugs.md Status cell may only close a bug when it NAMES the verification ("fixed — verified on prod <date>", "closed — watched working on staging"). A bare "fixed" / "merged" / "resolved" with no named check renders on her dashboard as an amber "Fixed, sanity check still owed" strip — visible until someone actually watches the repair work (`lib/bugs.js bugCheckState`). Exceptions that close without a test: superseded, won't-fix, not-a-bug, duplicate. When you fix a bug, the sanity check is PART of the fix, not a follow-up.

**ALL board text Divya reads is plain-first with the technical spec folded (BLOCKING, Divya's ask 2026-07-09).** Promises, Report-card plain sentences, Blocked-on-Divya items, and detour plain-story lines are written in kitchen English **with a concrete example wherever it helps** ("Example: you ordered 5 dozen, the bill says 60 pieces — the screen shows both"). The precise technical contract goes in a trailing `(For the team: <ids, files, flags — condensed but complete>.)` — her dashboard folds that behind a small "for the team" toggle. Never delete technical content to make text plain; MOVE it into the tail. A promise she can't read is a defect even when the build is perfect.

## Resume ritual (BLOCKING — first 60 seconds of EVERY invocation, every command)

0. If `docs/superpowers/modules/<slug>/` does not exist: STOP — tell Divya to run `new` or `adopt` first. No other command may invent a board.
1. Read `scoreboard.md` + all phase cards for the module.
2. Verify board vs reality:
   - `git -C <main> fetch origin --prune`
   - Merged-but-unclaimed work: `git log origin/dev --oneline --since="<last_verified>" -- <sweep_paths>` + `gh pr list --state merged --search "<sweep_keywords>"` (both stored in `blueprint.md` front-matter — widen them there if work ever slips the net) → any hit with no board entry = **unclaimed work**: adopt it onto the board (new row or promise annotation), flag it in the report.
   - Stale claims: for each 🔧 card, `git log -1 --format='%cr' origin/<branch>` (and does the branch exist?). No commits within `stale_hours` (scoreboard front-matter, default 48) → mark 🚨 on the scoreboard.
   - Phantom dones: any card claiming built/closed whose PR never merged (`gh pr view <PR>`) → mismatch. ALSO: any 🔎/awaiting-merge/"clean-mergeable" card whose OPEN PR has a red or missing CI/Vercel build gate (`gh pr checks <PR>`) → mismatch (a "clean" ruling over a red build is invalid — see reconcile §). Flag stale open PRs (many commits behind `dev`) too — the build that once passed may not reflect current dev.
   - DB check only when the module has migrations in flight: verify claimed migrations exist in the target DB per CLAUDE.md's verification query.
3. **Check `docs/superpowers/modules/<slug>/divya-notes.md`** (written by the local Conductor Dashboard, if Divya uses it — see `docs/superpowers/specs/2026-07-06-conductor-local-dashboard-design.md`) for any entries newer than `last_verified_against_git`. Surface every new note verbatim, addressed to whichever module / wave / phase / promise it's attached to — these are Divya talking directly to the board and must not sit unseen. If no such file exists, skip silently (she may not use the dashboard).
4. Report mismatches, stale claims, open detours, and new dashboard notes FIRST — before doing anything else.
5. Update `last_verified_against_git`, then proceed with the requested command.

## Commands

### Bare `/conductor` (no command, no module given)

1. List every folder under `docs/superpowers/modules/*/` that has a `scoreboard.md`.
2. Read each one's top-line status (current wave, any 🚨 stale or 🙋 blocked-on-Divya flags).
3. Present as a menu and ask what she wants to do — never assume, even if only one module is active:
   ```
   📋 Active modules:
   1. checklists — Wave 3 of 5, 🚨 1 stale
   2. hq-headquarters — Wave 2 of 4, all clean
   3. stock-picker — Wave 1 of 2, 🙋 blocked on you

   Which module, and what do you want — status / run / dispatch / housekeeping / something else?
   ```
4. If no `docs/superpowers/modules/*/` folders exist yet, say so and offer `/conductor new <module>`.

### `/conductor new <module>`

1. Invoke Skill(brainstorming) at MODULE altitude (the whole job, not a slice). Output feeds the blueprint: job sentence, scope in/out, "finished means" (including Divya's human items), phase list with one-line promises, dependency map.
2. Build the wave table: wave = 1 + highest dependency's wave; same-file phases never share a wave.
3. Ask Divya the kickoff questions in ONE phone-prompt message: gate level (run-ahead ⭐ default / gate-every-phase) + blueprint approval.
4. On approval: create the board folder from templates — `blueprint.md`, `scoreboard.md` (all phases ⬜), one card skeleton per phase (promises `PENDING` until that phase's plan exists), empty `debt.md`, `detours.md`.
5. Snapshot the board (per § Commit rhythm — never a main-checkout commit). Report: board path + phase table + "wave 1 is unlocked — `run` or `dispatch` when ready."

### `/conductor adopt <module>`

0. **Existing-board check (BLOCKING, before ANY sweep):** list `docs/superpowers/modules/*/` and check for a board already covering this module under ANY name variant (hq/headquarters, checklists/daily-checks…). If one exists: STOP the adopt — read that board and RESUME it (status/extend), never create a second. Two boards for one module is the exact muddle this skill exists to kill.
1. Announce the BOUNDED input set before reading anything, in chat: (a) `docs/superpowers/specs/` + `plans/` files matching the module slug/keywords, (b) module PRs + epic issues via `gh` search (title/label/paths), (c) memory-index entries matching the module, (d) actual code + preview-DB state. Nothing outside the set.
2. Sweep read-only (audit posture — for a deep or contested intake, invoke Skill(audit) itself). Build the promise inventory: everything ever promised, vs what verifiably exists.
   **Three verdict levels — name the level, never blur them:** (1) PROMISED (in a doc), (2) BUILT (existence-verified: code+DB+merged PRs), (3) WORKING (behavior-verified: a live walk or live data check of the real flow). Adopt-mode historical ✅ is level-2 unless a live walk backs it — the card and the intake report MUST say which. Every adopted board gets a prove-it-live phase for level-3, and where feasible the intake itself spot-checks ONE core live behavior (level-3) of the module's main daily loop.
3. Anything not verifiable inside the input set = an explicit **unverified** row. Never silent, never endless digging.
4. Draft the retroactive blueprint + board: phases marked ✅/⚠️/🔧/⬜/unverified, all owed items (migrations, smokes, U3s) as debt rows with `PENDING` sign-off; any live-behavior defects found go to `bugs.md`, not the debt table.
5. Present the intake report card to Divya (sources read, statuses, debt list) — the phone-readable block in chat, AND a RENDERED page (Artifact) of the full board whenever she must read board files to decide. File paths NEVER count as "presented" (her environment doesn't render them — global rule). She ratifies → snapshot the board (per § Commit rhythm). Nothing runs before ratification.

### `/conductor run <module> [phase]`

1. Resume ritual. Then pick the target: named phase, else lowest-numbered ⬜ phase in `current_wave`.
2. If the phase's plan is `PENDING`: invoke Skill(writing-plans) for it, then fill the card's Promises from the plan (each promise specific and verifiable — "screen X shows Y", "API returns Z", never "improve W").
3. Claim the card (this session). Build through the existing chain IN A WORKTREE: Skill(scenario-mapping) first → TDD → Skill(gap-check) before PR → PR to dev (never merge to main).
4. PR review loops via Skill(receiving-code-review). **If the phase touches a critical flow (CLAUDE.md's list) or any auth/RLS/access-control/cross-tenant surface, also run `/security-review` as an independent fresh-eyes pass BEFORE merge — BLOCK/FLAG/PASS, never skipped for that class of change, dispatched to an agent that did not build the phase.** This is Conductor's OWN gate — it does not touch or depend on `docs/dba/`'s Security Auditor (that fleet is a separate org; see [[project_kitchenhq_dba_org_vs_conductor]]). Reconcile (section below) runs ON THE OPEN PR — merge only AFTER the report card (and any required security-review) passes. Then close ✅, or gaps → fix now / debt with Divya's sign-off. (A merge that slips in early does not skip anything: the phase stays 🔎 until reconciled, and the breach is logged.)
5. **Auto-advance:** under run-ahead, continue to the next ⬜ phase in the SAME wave in this session. Finishing a wave NEVER silently starts the next — report "wave N complete" and wait for Divya to launch the next (run-ahead governs phases within a wave, not waves).

### `/conductor dispatch <module>`

1. Resume ritual. Confirm which phases in `current_wave` are ⬜ and have plans + promises filled (if not, write those plans first — a dispatch prompt without promises is un-reconcilable).
2. For each: mint a prompt from `reference/dispatch-prompt.md`, filling every token (pinned SHA from `git rev-parse origin/dev`, plan path, promises copied from the card, worktree/branch names per house convention).
3. Save each to `docs/dba/prompts/conductor-<slug>-phase-NN-<date>.md` AND paste each in chat.
4. Report the launch order: "these N can run together; wave N+1 unlocks when X merges."

### `/conductor status <module>`

Resume ritual (that IS most of the work), then report in EXACTLY this phone-readable shape:

```
📋 <MODULE> — <date>
Wave <N> of <M>

✅ done-clean:    NN <name>, NN <name>
⚠️ done-w/debt:   NN <name> (D2)
🔎 awaiting-check: NN <name> (PR #123)
🔧 in flight:     NN <name> — <owner>, <branch>, last commit <age>
🚨 stale:         NN <name> — quiet <X>h, needs release/chase
⬜ not started:   NN, NN
🔀 detours open:  <N> (latest: <one-liner>)
🐛 bugs open:     <N> (worst: <one-liner>, status)
💳 still owed:    <N> items, <N> awaiting your sign-off
🙋 blocked on you: <the 1-3 things only Divya can do>
⚡ mismatches:    <board-vs-reality findings, or "none — board matches git">
```

No prose essay. This block, then stop (add one ⚡ paragraph only if a mismatch needs explaining).

### `/conductor close <module>`

1. Resume ritual. Then the close checklist — ALL must pass:
   - Every phase card ✅ closed-clean, or ⚠️ with every debt row `paid` or `forgiven` (signed).
   - `debt.md` has zero `open` rows; zero `PENDING` sign-offs.
   - Zero open detours.
   - Blueprint's "finished means" walked item by item — including Divya's human items (verified done, not assumed).
   - Optional (offer it): Skill(audit) final health-check.
2. Any failure → report exactly what blocks close; do NOT close partially.
3. On pass: mark the scoreboard `MODULE CLOSED <date>`, snapshot, PR the snapshot branch into `dev`, and give Divya the closing report: promises made vs kept, debt paid vs forgiven, detour count.

### `/conductor housekeeping`

Repo-wide, NOT module-scoped — this is Conductor's own repo-hygiene sweep, the equivalent of a "Repository Steward" but owned entirely by Divya's side of the house (never touches `docs/dba/`; see [[project_kitchenhq_dba_org_vs_conductor]]).

1. Sweep, read-only, and report before touching anything:
   - `git worktree list` vs `git branch --merged origin/dev` — worktrees whose branch is already merged, or whose last commit is older than 48h with no open PR, are cleanup candidates.
   - `git branch --merged origin/dev` (excluding `dev`/`main`) — merged local/remote branches still lying around.
   - `pgrep -fl chrome-devtools-mcp | wc -l` + `sysctl vm.swapusage` — flag if helpers have piled up (per CLAUDE.md's global housekeeping rule).
   - `lsof -nP -iTCP -sTCP:LISTEN | grep node` — flag stale `npm run dev` / watch-build processes, especially any tied to a worktree that no longer exists or is already merged.
2. Present the candidate list to Divya in the phone-readable shape below — nothing is deleted without her go-ahead, per the global "confirm before anything hard to undo" rule.
3. On her confirmation, clean up: `git worktree remove`, `git branch -D`, `pkill -f chrome-devtools-mcp`, `lsof -ti:<port> | xargs kill` — only the items she confirmed.

```
🧹 HOUSEKEEPING — <date>
Worktrees to remove:   N (<name> — merged #123, idle 4d) ...
Branches to delete:    N (<name> — merged, idle 6d) ...
Chrome-devtools helpers: N running (swap: X%) — safe to pkill
Stale dev servers:     N (port <port>, worktree <path/gone>) — safe to kill
Confirm which to clean up, or "all".
```

## The meaning contract (logic-level verification — runs WITHOUT a human walk)

Storage is not behavior. For EVERY field, setting, toggle, time, or control a phase creates or touches, three questions must be answered in writing — in the phase plan, and re-verified at reconcile:

1. **MEANING:** what does this thing's existence promise the user? Enumerate every implication ("available-from 7 PM" implies: not a live card before 7, no ticks accepted before 7, overdue maths ignores pre-window hours).
2. **ENFORCEMENT:** for each implication, the exact code line that enforces it. Stored-and-displayed is NOT enforcement; a value consumed only by an ORDER BY is a confession, not a feature.
3. **PROOF:** each implication maps to its own test, written before the code (TDD).

The reconciler walks the diff FIELD BY FIELD asking these three questions — independent of the promise list — because the promise list can be complete while a field's implications are silently dropped (the 2026-07-06 B1 root: `available_from_time` stored since January, enforced never). An implication with no enforcer = ❌ gap → the two exits (fix or signed debt), same as any promise.

## The reconcile (the conscience)

- Runs when a phase's PR lands; also inside `adopt` intake and the `status` sweep.
- **Tier every fan-out (cost rule, 2026-07-15):** mechanical stages — inventory reads, file sweeps, smoke walks — dispatch on Sonnet / low effort; judgment stages — reconcile verdicts, adversarial verify, design review — on Opus / high. In Workflow scripts set `model`/`effort` PER STAGE, never one flat tier across a whole fan-out (that flat tier is the single biggest avoidable token bill on multi-agent runs). Fable only when Divya names it for the job.
- **Fresh eyes only:** dispatch a separate agent that did NOT build the phase (per the house model split, dispatch it as an Opus-model agent — judges are never the builder). Give it: the card's promises, the PR diff, the plan path. It walks promise by promise: **✅ built / ⚠️ built-differently / ❌ missing**, each ✅ with evidence (a test run, a screenshot, a walked flow) — never the builder's claim alone.
- **Then the meaning-contract pass (§ above):** the same reconciler re-walks the diff field by field — every touched field/setting/control gets its implications enumerated and each implication traced to an enforcing line + test. This is pure reasoning over the code; it needs no human and no live environment, and it catches the stored-but-never-obeyed class the promise list can miss.
- Gaps have TWO legal exits: fixed before close, or a debt row with Divya's explicit sign-off. Filing debt always requires her answer — under run-ahead this is a HALT, not a drive-by note.
- **CI/build gate is BLOCKING before any "clean / mergeable" ruling.** A green vitest run + preview probe is NOT a green build — vitest (esbuild) and `tsc --noEmit` both miss the type-narrowing class the full Vercel build catches (CLAUDE.md names the Vercel PR build as the authoritative type gate). Before ruling a PR clean or mergeable, READ its CI status (`gh pr checks <PR>` or `gh pr view <PR> --json statusCheckRollup,mergeStateStatus`) and confirm the Vercel build is green. A red or missing build gate is an automatic ❌ regardless of local test results — never "clean, mergeable" over a red build. (2026-07-08: #2227 was ruled CLEAN while its Vercel type-check had been RED since it opened — evidence was vitest + probes only.)
- The reconciler's verdicts are leads until evidence-backed (advisor's rule: sub-agent claims are not evidence). Spot-check at least one ✅ yourself before closing.
- **Author the plain-English columns for the local dashboard (per promise).** After the technical verdict + evidence are recorded, fill the phase card's three trailing Report-card columns (`Plain verdict` / `Plain sentence` / `Confirmed`) following `templates/phase-card.md`'s rules — so [[project_conductor_dashboard]] stays readable to Divya. Honest mapping: `built-untried` for a promise verified only at code/existence level (Level-2, not walked live), `live-works`/`live-broke` ONLY when the RESULT was actually watched happening (never award live-works for "it's in use" — usage ≠ verification), `not-checked` for anything unverified. The plain sentence is one kitchen-language line (no file paths / code names / PR numbers / migration ids / "database"); a live verdict must name test-copy vs live-restaurants. Mark `Confirmed: draft` when it's your first-pass summary, `yes` once the checker confirms it. Never auto-derive the plain verdict from the technical `✅/⚠️/❌` — an absent/blank plain verdict correctly shows "Not checked yet" on the dashboard rather than a guessed badge.
- **Author the `## At the pass` after-build checklist (the ticket's back side).** Fill the phase card's `## At the pass` section (per `templates/phase-card.md`): for each of the 7 standard checks (Smoke test / Walked it live / Your sign-off / DB change live / E2E test / Support docs / Released) set `done` / `owed` / `na` HONESTLY (owed = still to do; never a fake `done`). For every check that isn't already done, write the plain how-to under it — `who:` (you = Divya, or an agent), `do:` numbered PLAIN-language steps (real screens/taps, no jargon), and `done:` what the result looks like — because you just built it, so you know how to check it. This is what lets Divya tap a check on the dashboard and see exactly what to do (or hand it to an agent). A phase isn't truly "served" until its pass checks clear — leaving them honestly `owed` is the point, not a failing.

## Gate levels

Set at kickoff in `scoreboard.md`, changeable anytime by Divya:

- **run-ahead (default):** phases run back-to-back within the unlocked wave. Always stops for: genuine forks, any deviation from the approved blueprint (global flag rule — Designed/Built/Why/Options shape), anything risky or hard to undo, any reconcile gap needing a debt sign-off, wave boundaries.
- **gate-every-phase:** each phase ends with its report card and waits for Divya's ✅.

## Detours

When a bug/firefight interrupts module work: Skill(debugging-protocol) handles the bug itself; the Conductor (or the interrupted agent) writes a detour entry — what interrupted, phase affected, exact state, resume bookmark. Every `status` and resume ritual surfaces open detours until the bookmark is picked back up. If module work must move to another session mid-phase (context full, blocked), use Skill(handover-prompt) and note the handover on the phase card.

## Safety rails (inherited, never weakened)

Worktree isolation for every build · migrations preview-first and idempotent · no auto-merge to main · no production DB changes · release notes + plain-language PR rules · Gates 1–7 and U1–U4 apply to every phase spec/plan · `prod-migrations-before-dev>main` discipline tracked as debt rows so it can't be forgotten · `/security-review` required before merge on any critical-flow/auth/RLS phase · `housekeeping` cleanup never runs without Divya's explicit confirmation · this skill and everything it owns stays entirely separate from `docs/dba/` (Zahid's TD/MS/RS/SA/CA fleet) — see [[project_kitchenhq_dba_org_vs_conductor]].

## Self-improvement loop (BLOCKING, same-session)

Any miss → log in `failures.md` + patch this SKILL.md in the same session. Tripwires:

| Tripwire | It means |
|---|---|
| A phase turned out half-done AFTER its card said ✅ | Reconcile evidence bar too low — tighten it |
| Work landed in module territory that the sweep didn't catch | Sweep's path/keyword net too narrow |
| A stale claim sat unflagged past `stale_hours` | Resume ritual skipped or shortcut |
| A dispatch prompt failed cold in a fresh window | Prompt template is missing context — fix the template |
| A skip shipped without a debt row | The two-exits rule was bypassed — find the third door and brick it up |
| Divya asked "where are we on X?" and the status answer was wrong | Board-vs-reality verification gap |
| A detour never got an entry / never got resumed | Detour discipline failed |
| Divya was asked to decide on something she couldn't see (file links instead of a rendered view) | Presentation gap — deliver an Artifact/live URL, never bare paths |
