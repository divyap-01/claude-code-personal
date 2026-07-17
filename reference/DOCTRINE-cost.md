# The Cost Doctrine — read before any debug or fix job

**Ratified 2026-07-13, after PR #2539.** Every agent below has a named duty in it. This
is not advice; two of the four rules are enforced by `~/.claude/hooks/agent-guard.py`.

## What happened (the evidence, not a vibe)

Fleet driver-run, 2026-07-11 → 07-13. **~35 hours. ~55% of a weekly token budget.**

- **The fix took 48 minutes.** Commits 1–30. All five original bugs. Clean.
- **The other 70 commits were rework**, and their own titles confess it:
  *"F1 re-opened"* · *"the third door"* · *"the legacy delivery-receive door"* ·
  *"bulk receive door"* · *"close every OTHER door the lemon could still escape through"* ·
  *"kill the last duplicate pull_out rule"* ·
  **"guard the shipment-id chokepoints, not each caller by hand"** ·
  **"make addStopToTrip/recordPickup structurally safe, not caller-dependent"**

Those last two ARE the correct architecture. We reached them on **commit 87 of 100**.

- **22 security-audit rounds** — not because the code was dangerous, but because **the diff
  never stopped moving**. Every fix folded into the branch invalidated the last audit and
  bought another full round.
- **Divya found 5 of the 13 bugs herself, by hand, one at a time** — each one triggering a
  fresh build → audit → verify cycle. The test suite (~4,900 green), the audits, and four
  cold walkthroughs found **zero** of them.
- **We inflicted two on ourselves**: the "failed read ≠ empty" fix recreated the exact
  dead-end trap the project existed to kill; the clamp fix and the pull-out fix silently
  cancelled each other out.

## The rule under all of it

The code this very PR shipped carries this line:

> **"A guard the caller must remember to call is a guard that will eventually not be called."**

**It is just as true of process as of code.** A process rule you have to *remember* is one
you will *not* follow — at 4am, on commit 60, when patching the route in front of you feels
faster. So: walls, not intentions.

---

## The four rules

### 1. Close the bug list BEFORE writing a line. (`smoke-tester`, `debugger`)
Drive the **entire flow**, both faces, on preview, and return **all** the breakage — before
any fix is designed. One sweep. **If Divya finds a bug after we've built, that is the tell
that this was skipped.**

### 2. Name the CHOKEPOINT before coding. (`debugger`, `planner`, `builder`)
Every fix brief must answer, in writing:
> **"Where is the ONE place this rule lives, and what are ALL the doors into it?"**

*"I'll patch this route"* is a **STOP**, not a plan. Guard the **exits**, not the entrances.
Seven writers could set an order `ready`; only four shipment-creators moved food and money.
Gating those four made a missed entrance harmless. **~25 commits on #2539 were the same rule
being re-applied to a door nobody had gone looking for.**

### 3. The branch FREEZES when its PR ships. (`pr-shipper`, `builder`, `security-auditor`)
A new finding is a **new PR**. Always.
**Enforced — Wall 3.** The freeze marker is written automatically by the PR gate the moment
a PR is cleared, so nobody has to remember to set it. Docs and merge-conflict resolution are
exempt. Divya may override (`~/.claude/.allow-frozen-branch`) — **that is her call to make,
never yours to assume.**

### 4. The box: 2 hours. (everyone, and above all the main conversation)
**Enforced — Wall 4.** More than 2 hours since Divya last spoke → **agent/workflow dispatch is
blocked.** Reading, editing, committing still work, so nothing can be stranded mid-merge.
The clock is reset **only by her typing** — a box you can reset yourself is not a box.

When the box expires, report in four lines and let her choose (extend / split / park):
> **DIAGNOSED** · **FIXED & verified** · **STILL OPEN** (the list — not a promise to keep going) · **COST so far**

### 5. And the one thing that went RIGHT — keep doing it.
Gemini's review found 2 issues. Asking **"what is the SHAPE of this bug, and where else does
that shape live?"** found **ten** — including an unchecked read that could soft-delete
in-progress cook stages. Nine were fixed in one sweep.

**Every confirmed bug ends with the shape question. Sweep once. Never one-by-one.**

### 6. Findings travel as FILES, never as retellings. (everyone)
A sweep's deliverable is a findings file — `~/.claude/handoffs/YYYY-MM-DD-<topic>-findings.md`,
one line per finding with a STATUS column (`OPEN` / `FIXED <sha>` / `RETESTED`). The tester
writes it, the builder flips items to FIXED as each fix lands, the single re-test flips the
rest, the lane links it. Downstream agents read the FILE — a summary is a pointer, not a
source. (The relay is lossy; files are not. And the next session trusts the file instead of
re-sweeping everything.)

**Board discipline applies (the START-HERE lesson):** these files are machine-global — every
session can read them — so NEVER rewrite one wholesale. **Creator creates; everyone else edits
only their own rows** (surgical Edit on the STATUS cell, never a full-file Write). If your
intended filename already exists and isn't yours, suffix it (`…-findings-2.md`) instead of
overwriting. The handoffs dir is git-snapshotted at every session end, so even a clobbered
file is recoverable — but recoverable is not an excuse.

### 7. Briefs are contracts. (the conductor, above all)
Every dispatch carries: **exact file:line anchors** (never "find the shipping screen"), the
**paths** of the plan/findings files to read, the **loop shape** expected (one sweep →
complete list → one batch → ONE re-test), and a **don't-read-beyond scope**. An agent handed
a brief without anchors may bounce it — that is the system catching a lazy brief before it
burns exploration tokens, not insubordination.
