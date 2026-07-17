# audit — failure log (incident book)

Every audit-process failure gets an entry, logged in the same session it's noticed (see "Self-Improvement Loop" in SKILL.md). Format per entry: **date • module • tripwire • what the audit said vs what surfaced • patch produced.** An entry with no patch line is itself a violation.

---

## 2026-07-06 • LIVE (Divya) — scheduling permissions audit • a production WRITE-probe was drafted in a read-only engagement (near-miss; rail caught it)
- **Tripwire (safety rail):** while verifying RLS on production, the auditor wrote a diagnostic script that included an anon `UPDATE … eq(id, non-existent)` probe against the production `profiles` table (intent: test whether anon writes are blocked). The auto-mode safety classifier denied it before execution. **No production write occurred**, but a mutating statement should never have been aimed at production during a SELECT-only engagement.
- **What happened:** the auditor conflated "prove the write path is blocked" with "attempt a write." A read-only engagement proves write-exposure from the POLICY text (and, at most, an authenticated read), never by firing a mutation at prod. The empirical anon *read* (which cleanly proved the profiles leak, SCHEDPERM-004) was the right tool; the write-probe was gratuitous.
- **Patch produced:** added an explicit rail to SKILL.md — "Never draft a mutating statement against any target, even a guaranteed-no-match one, to 'test' whether writes are blocked; write-exposure is asserted from the policy body (and disclosed as not-runtime-proven), never probed." Recorded here so the near-miss can't graduate to a real breach next time.

## 2026-07-03 • LIVE (Divya) — audits started without asking WHERE they should run • scoping miss (first real firing of this loop)
- **Tripwire:** the user learned only after results arrived which target an audit had used — "this audit was done on dev, but what I actually want is on production." The skill hardcoded `origin/dev` + both DBs and asked only WHICH module, never WHERE.
- **What happened:** an entire engagement's relevance depended on a default the user never chose; discovering the mismatch post-hoc wastes the whole run.
- **Patch produced:** the BLOCKING "Scope question FIRST" prompt (which code: dev tip / production / local working copy; which data: preview / production / both; one-tap combos "Live health check" and "Pre-merge check"); "Pin the code FIRST" made target-aware (pins the CHOSEN ref, incl. local-copy snapshots with dirty-state disclosure); the mismatched-generations rule (schema drift checked against migration state before being called a bug); new tripwire row for scoping misses.

## Pre-log incident (the freshness wound, from recorded feedback)
- Analysis/audit agents were found reading the STALE main checkout (old branch, days behind, another session's dirt) instead of fresh `origin/dev` — findings cited code that no longer existed. Recorded as standing feedback (`feedback_analysis_agents_need_fresh_worktree`, `feedback_fresh_pull_before_reporting` — Divya's #1 frustration).
- **Patch produced (2026-07-03):** the "Pin the code FIRST" BLOCKING section — fetch, pin the `origin/dev` SHA, audit a read-only snapshot/worktree of that SHA, state it in the report header, leave dirty checkouts untouched.

## 2026-07-03 • skill-text contradiction found during baseline test • rails fought the right behavior
- **Tripwire:** the "no worktrees" safety rail (meant to ban mutation) also banned the read-only freshness mechanism the standing feedback demands — the baseline agent had to improvise a resolution mid-engagement (git-archive snapshot at a pinned SHA) and flag the collision itself.
- **What happened:** two rules collided; obeying both letters was impossible as written. A rule that forces improvisation will be resolved differently by different sessions.
- **Patch produced:** rail reworded (read-only snapshot/worktree explicitly required and explicitly not a violation; editing or committing inside one is).

## 2026-07-03 • baseline test (pre-upgrade), staged /audit checklists • excellence was improvised, not enforced
- **Tripwire (meta):** the baseline agent independently invented the pinned-SHA snapshot, the prior-audit disposition table with re-verified "fixed" claims (dev vs production separately), the lead-vs-finding refutation walk for a suspicious NULL rowset, semi-blind contamination disclosure, and the cron live-fire check — NONE of which the skill text demanded. On a weaker day, in a foreign project, or with a lighter model, all of it silently disappears.
- **What happened:** skill relied on model judgment + project context for its best behaviors.
- **Patch produced:** all of the above codified — "Pin the code FIRST", workflow step 5 (re-audit disposition), the lead-vs-finding five-step refutation discipline + Critical/High self-refutation rule, the severity rubric, the gap-check lens with the cron sub-checklist and live-fire check, semi-blind disclosure, sub-agent-claims-are-leads, whole-app/UI-only scope rules, and the Self-Improvement Loop + this incident book.

## 2026-07-11 — commissary recipe-dishes audit: FALSE POSITIVE published (REC-001)

- **Module:** commissary pack sizes / recipe dishes.
- **Tripwire:** "A published finding proves to be a false positive." REC-001 claimed 9 offered dishes were unorderable because their recipe `yield_unit` is a container name ("Full Deep Aluminum") that the pricing engine can't convert. Divya was told this in chat AND it went into a team-facing message. It is wrong: 0 of 9 are unpriceable.
- **What the audit said vs what is true:** `resolveSourceUnitsPerPack` (lib/sale-items/pack-size-pricing.ts:72-95) tries an **exact string match between pack unit and source unit BEFORE the unit-family lookup**. 8 of the 9 dishes sell in exactly the unit they are cooked in, so the match succeeds and they price fine. The sub-auditor asserted the pack unit was `'ea'`; it is in fact the same container string.
- **Root cause of the miss (two):** (1) I re-verified the sub-auditor's *conclusion* against `sale_items.pack_uom` — but the engine reads `sale_item_pack_sizes.pack_uom`, a DIFFERENT column. Verifying against the wrong column is not verification. (2) I read the code's failure branch (`getConversionFactor` → null) without reading the branch ABOVE it that short-circuits.
- **Excuse used (verbatim thought):** "two independent auditors both flagged unit mismatches, and the container names are obviously not real units — this is clearly right." Two auditors agreeing is not evidence; they shared the same wrong premise.
- **Patch:** SKILL.md — added to Common mistakes + a rule under Method: before publishing a finding that a code path FAILS, read the whole function including every early-return/short-circuit branch above the failing line, and re-verify against the exact column/field the code reads (not a same-named sibling column on a parent table). See same-date edit.

## 2026-07-11 — commissary pack sizes: FLIP-FLOPPED on the money finding (twice)

- **Module:** commissary pack sizes.
- **Tripwire:** "A published finding proves to be a false positive" — applied to a RETRACTION. A sub-auditor found under-billing (buyers charged `base_price / packs_per_case`). I first relayed it as real ($312 of live under-billing). Then I "corrected" it to *no money lost*, on the reasoning that the tray price exactly matched the tray cost, so the tray must be the product. Then the owner said: *"Satellite should not order one tray — the commissary sells 75 naans."* The original finding was right; my retraction was the false positive.
- **Root cause of the miss:** I inferred a BUSINESS SEMANTIC (what is the sellable unit?) from an arithmetic coincidence in the data, instead of asking the one person who defines it. `$2.51 == cost × 15` is a fact about arithmetic, not evidence about what the commissary sells. Both of my conclusions were "supported by the numbers" — the numbers cannot settle it.
- **Excuse used (verbatim thought):** "the tray price matches the tray cost so neatly that the tray must be the product — pricing is correct, only cooking is wrong."
- **Cost:** two contradictory reports to the owner in consecutive turns, plus a team-facing message that had to be corrected twice. Trust cost, not just time.
- **Patch:** SKILL.md — new rule under Method: a finding that turns on what a business unit MEANS is an OWNER question, never an inference from data. See same-date edit.
