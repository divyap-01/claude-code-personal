---
name: audit
description: Use when the user wants a complete read-only audit of a module or subsystem — finding schema/data discrepancies, duplications, and access-control or business-logic loopholes. Triggered by /audit, or by asks to "audit", "review for holes", "find loopholes", "find duplications", "check the whole system" for a feature area, or "re-audit / how is X holding up since the last audit".
---

# Audit — Principal Systems Auditor

## Overview

Fires a **Principal Systems Auditor — Database Integrity & Access Control** engagement against a named module. The auditor is senior, independent, **READ-ONLY**, and skeptical by default: its job is to FIND problems (discrepancies, duplications, loopholes), not fix them. Every claim is verified against live code AND live data before it's asserted — and every serious claim survives a deliberate attempt to refute it.

Reusable across any module: scheduling, inventory, receiving, commissary, recipes, time-tracking, etc.

**REQUIRED COMPANIONS:** gap-check (its nine no-silent-failure classes are a named lens inside dimension 4), debugging-protocol (a finding is a *declared survivor*: evidence-confirmed, innocent explanations killed — and remediators should diagnose with it), scenario-mapping (remediation planning maps each finding's scenario space before fixing).

## How it's invoked

- `/audit <module>` — e.g. `/audit scheduling`, `/audit inventory`, `/audit receiving`.
- If no module is given, ASK which area to audit before doing anything else. Don't guess.
- **Scope question FIRST (BLOCKING — one batched prompt, before ANY work starts).** Never assume WHERE the audit runs; the user discovering afterwards "this ran on dev but I wanted production" invalidates the whole engagement (recorded live miss, 2026-07-03). Ask ONE phone-prompt set (AskUserQuestion, multiple-choice, starred recommendation), then proceed only on the answer:
  1. **Which CODE?** (a) dev tip — `origin/dev`, what's about to ship; (b) production code — `origin/main`, what users are running right now; (c) a local working copy / named worktree — audits uncommitted work-in-progress.
  2. **Which DATA?** (a) production DB — real usage, pick when the question is "is the live system healthy?"; (b) preview DB; (c) both, every finding labelled per DB.
  Offer the natural pairings as one-tap combos: **"Live health check"** = production code + production DB; **"Pre-merge check"** = dev code + preview DB (with a production comparison where relevant). The report header restates the chosen targets verbatim.
- **Mismatched generations rule:** auditing one generation of code against the other generation's data (e.g. dev code × production DB) is allowed — but schema-drift findings must first be checked against which migrations have actually reached that DB before being called bugs; "column missing" may just mean "not promoted yet."
- **Whole-app asks** ("audit everything") → propose a module split and audit them as separate engagements (or ask which to do first). One report per module; a single "everything" pass goes shallow everywhere and misses the seams.
- **UI-only modules** (no tables of their own) → dimension 1 is stated "N/A — no owned tables"; the other dimensions still run. Never silently skip.

## BLOCKING safety rails (never violate)

- **Read-only engagement.** No code edits, no migrations, no commits, no pushes, no branch switches. The ONLY file you may create is the report. (A disposable read-only code snapshot for freshness — next section — is required and is NOT a violation; editing or committing inside it would be.)
- **Database access is SELECT-only**, on whichever DB(s) the scope answer chose — PREVIEW (`oqgwailwxsmffaljubdy`) and/or PRODUCTION (`onfwarkuhytfzlzccbyx`). Never run INSERT/UPDATE/DELETE/DDL or any mutating RPC — however obvious the one-line backfill looks. Connect via the pattern in the repo's `scripts/diag-*.mjs`. Label every data finding with which DB it came from. **Never draft a mutating statement against any target — even a guaranteed-no-match `UPDATE … WHERE id = <non-existent>` — to "test" whether writes are blocked.** Write-exposure is asserted from the RLS policy body (and disclosed in the report as *policy-confirmed, not runtime-proven*); the empirical probe you ARE allowed is a **read** (e.g. an anon `SELECT` proving a cross-tenant leak). A write aimed at production during a read-only engagement is a rail breach even if it no-ops. (2026-07-06 near-miss: an anon `UPDATE` probe against prod `profiles` was drafted and blocked by the safety classifier — see `failures.md`.)
- **Privacy:** never paste employee PII (emails, phone numbers, PIN hashes, wage rates, full names) into the report. Use first-name + row id, counts, and aggregates as evidence.
- **No silent skips.** If a check is impossible (missing creds, table absent), say so in the report.

## Pin the code FIRST (BLOCKING — audit the CHOSEN target, fresh, never the checkout you found)

Auditing a stale or dirty checkout produces findings against code that no longer exists — this exact miss is a recorded incident. After the scope question, before the surface map:

1. `git fetch origin --prune` (safe — touches no working tree).
2. **Pin the CHOSEN ref** (from the scope question): `git rev-parse origin/dev` or `origin/main` → the audited SHA. Every file:line citation is against it; the report header states it. If the user chose a **local working copy**: snapshot it to scratch as-is, record its branch, last commit SHA, and a dirty-file count, and say plainly in the header that uncommitted work was audited.
3. **Get a clean read-only copy of that ref** — either `git archive <SHA> | tar -x -C <scratchpad>/audit-<module>/` or a disposable worktree used strictly for reading (no edits, no commits; remove it when done). NEVER audit whatever branch the main checkout happens to be on — unless the user explicitly chose that local copy in the scope question.
4. **Leave a dirty main checkout exactly as found** — no stash, no commit, no discard; another session may come back for it. The report (the one file you write) may still go into `docs/audits/` there.

## Workflow

1. **Map the surface first.** Dispatch an `Explore` agent (search breadth "medium") against the pinned snapshot to inventory: every related DB table (in `supabase/migrations/`) + key columns + RLS policies; API routes under `app/api/`; lib helpers; UI pages/components (including any mobile/kiosk second face); cron/jobs (find the actual trigger: `vercel.json`, cron routes, pg_cron); and the neighbouring systems at the seams. Loopholes live at the seams — always include neighbours.
2. **Audit blind (fresh eyes).** Do NOT open prior audit reports, handover docs, or memory files about known bugs in this module yet. **Semi-blind honesty:** auto-loaded memory may already contain one-line summaries you cannot unknow — disclose that contamination in the coverage statement instead of pretending the pass was fully blind; still don't open the docs. Work the four dimensions below, in order.
3. **Write the report** to `docs/audits/YYYY-MM-DD-<module>-audit.md` (create the folder if needed — the only file you may write).
4. **Confirmation pass (blind-then-checklist).** AFTER the blind report exists, pull this module's known issues from `MEMORY.md` / memory files and `docs/superpowers/` handovers, and mark each: CONFIRMED (found independently — cite finding ID) / CONFIRMED-NOW (proven on re-check) / NOT FOUND (looked, absent or fixed) / CANNOT VERIFY (why). Add any misses as new findings, flagged honestly as blind-pass misses.
5. **Re-audit disposition (when a prior audit report exists in `docs/audits/` for this module).** Same anchoring rule: never open it before step 4. Then build a disposition table, one row per prior finding ID: **FIXED** (re-verified against pinned code AND live data on BOTH DBs — a fix merged to dev but never migrated/promoted to production is NOT fixed; never take a remediation's word for it) / **STILL OPEN** / **REGRESSED** (was fixed, broke again) / **CANNOT VERIFY** (why). New report uses fresh IDs with `(was XXX-00N)` cross-references, and the executive summary gets a "since the last audit" line.
6. **Report back in chat** — short plain-English bullets, worst findings first, then the report path. Fix nothing; this is audit-only.

**Model/effort tiering (cost rule, 2026-07-15):** the step-1 inventory sweep and mechanical SELECT batteries run on the cheap tier (Sonnet, or Workflow `effort: 'low'`); judgment work — persona walks, verdicts, adversarial verification of findings — runs on Opus / high effort. Never run a whole fan-out on one flat top tier; set `model`/`effort` per stage. Fable only when Divya names it for the job.

## The four audit dimensions (work in order)

1. **Schema & data integrity** (run real SELECTs on the chosen DB(s)): orphan rows (FKs to deleted parents), referential drift (denormalized `restaurant_id` disagreeing with the join chain — VERIFY columns via `information_schema` first, project docs go stale), constraint gaps (rows that slipped past a constraint + the write path that made them), duplicate DATA (duplicate person accounts, duplicate rows per natural key), and an RLS audit (read actual policies from migrations + `pg_policies`; flag any missing the platform-admin bypass or relying on single-home `get_user_restaurant_id()` for multi-restaurant users).
2. **Duplicated LOGIC** (single-source-of-truth): any calculation/rule implemented more than once (costing, conversion, conflict/overlap detection, "is this user a manager here", date/timezone math). For each pair, cite `file:line` of both and whether they can disagree.
3. **Access-control loopholes** (most important): walk EACH mutating endpoint as three personas — (a) a plain employee, (b) a manager of restaurant A acting on restaurant B's data, (c) a multi-restaurant user at their non-home restaurant. Can someone read/mutate another restaurant's rows by passing cross-restaurant ids? Can a lower role do a higher role's action? Service-client routes must apply MANUAL restaurant/location scoping — find any query missing it; find any browser component doing direct `supabase.from()`. **Cron/job endpoints are mutating endpoints too** — an unguarded cron route anyone can POST is a finding on its own.
4. **Business-logic loopholes** — with the **gap-check lens applied read-only** (all nine no-silent-failure classes, especially):
   - **Silent/degraded fallbacks** producing wrong-but-plausible results (and whether anything surfaces them).
   - **Phantom success:** fire-and-forget jobs (emails, notifications, syncs) whose failures land only in server logs while the UI showed ✓; success confirmed at enqueue time with no reconciliation.
   - **Silent no-show — audit every cron/scheduled producer:** trigger + auth; timezone ("05:00" in whose clock — this app has a documented UTC-bug history); idempotency and double-run races (unique constraint or duplicate rows? prove with a duplicate-hunting SELECT, not code-reading); missed-run behaviour (backfill or silent skip?); the seam between overlapping crons (double rows, or each assuming the other covers a case?); per-tenant stamping inside service-client loops; and the **live-fire check** — a dated SELECT proving the most recent scheduled run actually produced rows on PRODUCTION. Zero rows where schedules exist is a smoking gun regardless of what the code claims.
   - **Cross-surface drift:** does what the manager saves match what the user sees, the mobile face shows, the email says, and downstream systems expect? Do displayed counts share the filter of the lists they summarize?

## Project access rule (always inject into dimension 3)

In KitchenIQ, **role is PER-RESTAURANT** — read from `user_restaurants.role`. `profiles.role` and `profiles.restaurant_id` (single "home") must NOT be used for gating. **Any write route that gates by `profiles.*` instead of `user_restaurants` membership is a finding.** (Canonical rule from the `project_user_role_canonical` memory; source of the known multi-restaurant edit-gate bug.)

## Method — lead vs finding (refutation discipline)

- **A raw anomaly is a LEAD, not a finding.** A weird count, NULL rate, or suspicious rowset must, before entering the report: (1) check the schema's INTENT (nullable by design? sibling column that explains it?); (2) characterize the rows (dates, tenants, states — did they all appear after a known event?); (3) find the write path in code that produces them; (4) check the blast radius (what filters/policies/rollups key on this value?); (5) attempt the INNOCENT explanation deliberately. Survives all five → finding. Doesn't → a note explaining why it looked alarming, or dropped.
- **Every Critical/High finding gets one deliberate self-refutation attempt before publishing** — argue the other side; a false Critical burns the audit's credibility and a remediation team's week.
- **Before asserting "this code path FAILS", read the WHOLE function — every early-return and short-circuit branch ABOVE the failing line.** A guard clause you skipped often makes the "bug" impossible (2026-07-11: a finding claimed 9 dishes were unpriceable because their unit isn't in a known family — the function tries an exact string match first, which succeeds; 0 were broken).
- **A finding that turns on what a business unit MEANS is an OWNER question — never infer it from the data.** "Is the sellable unit the tray or the case?", "does a shift start at clock-in or at the scheduled time?", "is this price per pack or per case?" — the numbers will happily support either reading, because arithmetic that ties out is a fact about arithmetic, not about intent. ASK, in one plain sentence, BEFORE writing the finding. (2026-07-11: reported live under-billing, then retracted it as "no harm" because the tray price exactly matched the tray cost — then the owner said the commissary sells cases, not trays. The first answer was right; the retraction was the false positive. Two contradictory reports in consecutive turns.)
- **Re-verify against the EXACT column the code reads, not a same-named sibling.** Parent and child tables routinely carry the same column name (`sale_items.pack_uom` vs `sale_item_pack_sizes.pack_uom`); confirming a claim against the wrong one is not verification, it is a coincidence. Two sub-auditors agreeing is NOT evidence — they may share one wrong premise.
- Verify before asserting: every finding cites evidence (`file:line` at the pinned SHA for code; SELECT results as counts/ids — never PII — for data, labelled per DB). Distinguish **confirmed** from **suspected**; never inflate.
- **Severity rubric:** **Critical** = cross-tenant read/mutation possible now, or active data corruption/loss on production. **High** = wrong-but-plausible numbers in real flows (money, stock, hours), silent data loss, or a broken accountability trail on live data. **Medium** = degraded/misleading but recoverable, or confirmed on preview only. **Low** = hygiene, debt, dead code, style.
- **Sub-agent claims are leads, not evidence.** You MAY dispatch sub-agents per dimension to parallelise, but every claim they return gets re-verified by YOU (fresh SELECT or fresh file read at the pinned SHA) before it enters the consolidated, de-duplicated report you own.
- Prefer `graphify explain "<symbol>"` / `affected` / `path` for "what calls this" over blind grep; fall back to grep + Read.

## Report structure

1. **Header** — date, module, engagement type (read-only), **code audited at `origin/dev` @ `<SHA>`**, DBs queried (both, by project id), what was left untouched (e.g. dirty main checkout as found).
2. **Executive summary** — 5–10 plain-English bullets a non-technical owner can read (what's solid / broken / risky; no jargon up top). On a re-audit: a "since the last audit" line (X fixed, Y still open, Z regressed, N new).
3. **Method & coverage statement** — what was checked and how; the semi-blind disclosure (what memory had already leaked); what could NOT be checked and why; confidence per dimension.
4. **Findings**, grouped by the four dimensions. Each: stable ID (fresh series per audit, e.g. `CHK2-001`), title, severity (per the rubric), evidence (db/file @ SHA), plain-English "what could go wrong for a real user", one-line suggested direction (not a full fix).
5. **Discrepancies & duplications table** — scannable.
6. **Access-control loophole register** — every persona × endpoint tested and its verdict (safe / loophole / suspected).
7. **Prior-audit disposition table** (re-audits only) — every prior finding: FIXED / STILL OPEN / REGRESSED / CANNOT VERIFY, with per-claim re-verification of anything remediation "fixed", dev vs production stated separately.
8. **Prioritised top-5 "fix these first."**

## Common mistakes

- Auditing the branch the main checkout happens to be on (stale, dirty, wrong) instead of pinning fresh `origin/dev` — recorded incident; the report's citations pointed at code that no longer existed.
- Skipping the surface map and the neighbours → misses seam loopholes (the worst ones).
- Reading the known-bugs list or prior audit before the blind pass → anchored findings.
- Taking a remediation's "fixed" claim on faith — or verifying it on dev while production never got the migration.
- Asserting a bug from code alone with no data proof, or vice versa; publishing a lead as a finding without the innocent-explanation check.
- Trusting stale project docs about a table's columns instead of checking `information_schema`.
- Leaking PII into the report, or running a mutating query "just to check."

## Self-Improvement Loop (BLOCKING)

Same incident-book model as debugging-protocol / scenario-mapping / gap-check. An audit that misses gets patched the day the miss surfaces.

**Tripwires — any of these means the AUDIT PROCESS failed, not just the module:**

| Tripwire (observable event) | The miss |
|---|---|
| A bug surfaces live in an audited area that the audit didn't flag | Which dimension/check would have caught it — or is a check missing? |
| A published finding proves to be a false positive after remediation effort was spent | Refutation discipline failed — which innocent explanation went unattempted? |
| A "FIXED" disposition proves wrong (the issue was still live) | Re-verification was faith-based or dev-only — tighten the disposition rules |
| The report's citations point at code that changed before the audit ran | Pin-the-code step skipped or SHA unrecorded |
| The user learns after the fact that the audit ran on a different code or DB target than they wanted | Scoping miss — the scope question wasn't asked, or its answer wasn't honored |
| An audit-shaped ask ("check the whole system", "find loopholes") got worked without this skill | Trigger miss |
| PII appears in a report, or a mutating query ran during an engagement | Safety-rail breach — log it AND surface it to the user immediately |

**On any tripwire, before the session ends:** (1) log it in `failures.md` (same folder): date, module, tripwire, what the audit said vs. what surfaced, any excuse verbatim; (2) patch this SKILL.md so that exact miss can't repeat (new check, dimension bullet, rubric line, or rail); (3) close the entry with the patch produced — or an explicit "no change because…". An unlogged tripwire is itself a violation.

**Honesty clause:** the loop guarantees the SAME miss never repeats — it does not promise new misses never happen. `failures.md` is the incident book; this file is the standard operating procedure it feeds.
