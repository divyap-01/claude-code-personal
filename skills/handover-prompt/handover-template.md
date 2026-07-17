# Handover — <Topic>

**Date:** YYYY-MM-DD
**Author:** prior Claude session (<user> driving)
**Mode:** FULL handover  |  SPLIT handover (this doc covers only Work B; Work A continues elsewhere)
**Status:** <one sentence — e.g. "Migration applied to preview; API done; UI half-built; 2 tests red.">

---

## TL;DR for the next agent

<2–4 sentences. What is this, where does it stand, what is the one job you're handing over.>

**The job (what "done" looks like):** <one sentence. For SPLIT, this is ONLY Work B.>

**Locked decisions (do NOT relitigate):**
- <decision already confirmed with the user>

**Open questions (ask before acting):**
- <genuine unknown that needs a human decision>

---

## First actions (do these before anything else)

<This project's setup ritual — sync, branch/worktree, env files, install deps —
copy-pasteable. Replace with whatever a fresh checkout of THIS repo needs.>

```bash
# Example (auntyskitchen) — adapt to this project:
git fetch origin --prune
git worktree add .worktrees/<feature> -b feat/<project>-<phase>-<topic> origin/dev
cd .worktrees/<feature>
cp ../../.env.test .env.test     # else test:run shows ~73 false env failures
npm install                       # fresh worktrees miss some deps
```

<Any other must-do-first step: read file X, pull env, check a DB row.>

---

## What's already done / shipped

- <PR #... merged to dev/main (SHA ...) — what it did, so you don't redo it>
- <migration applied? to which DB? verified how?>

## What's NOT done (your work)

- <concrete task — which file, which behaviour, how to know it's done>
- <the red tests and what they're telling you>

---

## Real file paths (re-verify line numbers — they drift)

- `path/to/file.ts` (≈ line N) — <what lives here / why it matters>
- <only paths you actually opened. If unsure a file exists, say "find the file that does X" instead of guessing.>

## Guardrails — do NOT

- <the load-bearing "don't": e.g. don't write a second write path; reuse `saveAlias`>
- (SPLIT only) Do NOT touch Work A — your scope is strictly Work B below.
- Do NOT claim it's fixed without the verify step below (CLAUDE.md §7).

---

## How to verify it actually works

- <run this test / do this real scan / check this DB row — the concrete proof>

## Project obligations

<Whatever THIS project requires alongside the code. Delete rows that don't apply;
add ones that do. Example obligations from auntyskitchen:>

- **Migration:** [<migration file>](supabase/migrations/<file>.sql) — apply to **preview and/or production** BEFORE the new code goes live; run `NOTIFY pgrst, 'reload schema';` after; verify the version row.
- **Gates:** <which project gates/checklists this work must address>.
- **Release notes / support docs:** <owed? plain-language release entry? a support topic to add?>
- **Memory:** update the relevant memory note as tasks complete.

---

## Why this unblocks Work A   (SPLIT handover only)

<1–2 sentences: what Work A is waiting on, and what B delivers that lets A resume.>

## Report back   (SPLIT handover only)

When Work B is done, report back: <the SHA / new endpoint name / migration version / whatever A needs> so Work A can resume.

---

## Repo state at handover

- Main checkout is on branch `<branch>` (<leave it alone / your base>).
- Worktrees: `<.worktrees/...>` created off dev / torn down / left in place.
- Uncommitted work: <none / describe>.
