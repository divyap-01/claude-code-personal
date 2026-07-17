# Conductor — Failure Log

Same-session rule: any tripwire hit (see SKILL.md § Self-improvement loop) gets an entry here AND a SKILL.md patch in the same session — or an explicit "no patch because <reason>" note.

Format per entry:

## YYYY-MM-DD — <one-line miss>
- **What happened:**
- **Which tripwire:**
- **Root cause:**
- **Patch applied to SKILL.md:** <the change, or "none because …">

## 2026-07-06 — Intake board presented as file links; Divya couldn't see it
- **What happened:** First flight (`adopt checklists`). The ratification ask linked the board's markdown files; Divya answered "I can't see the board." Her global rule already says file links don't render in her environment — rendered pages/screenshots only.
- **Which tripwire:** none matched exactly (presentation-layer gap) — new tripwire added.
- **Root cause:** SKILL.md's adopt step 5 said "present the intake report card" without specifying the delivery medium; defaulted to chat block + file links.
- **Patch applied to SKILL.md:** adopt step 5 now requires the chat block PLUS a rendered page (Artifact) or live URL whenever Divya must read board files to decide — file paths never count as "presented." New tripwire row added to the table.

## 2026-07-06 — Intake ✅ verdicts read as "working"; Divya found live rot same-day (D18)
- **What happened:** Checklists intake marked history phases ✅/⚠️ on code+DB+PR evidence. Within the hour, Divya walked the live prod Today screen and found the overnight-window bug (last night's completions on tonight's card, no finalize-at-due, visible before ready-time) — a phase-01 surface whose card read ✅ built.
- **Which tripwire:** #1 — "a phase turned out half-done AFTER its card said ✅."
- **Root cause:** intake evidence proved EXISTENCE, not BEHAVIOR, and neither the cards nor the report named the difference.
- **Patch applied to SKILL.md:** adopt step 2 now defines three verdict levels (PROMISED / BUILT / WORKING), requires every card + intake report to name its level, mandates a prove-it-live phase on every adopted board, and asks for one level-3 spot-check of the core daily loop during intake itself.

## 2026-07-06 — Board unreadable to the owner: jargon, no bug register, no per-phase "checked live?" view
- **What happened:** Divya on the intake page: "debt register — I don't even understand what it is"; "I don't see a bug register"; "I don't see... a live walkthrough done or not, or the deviations from what was planned." The live bug (B1/D18) had been filed into the DEBT table because no bug register existed.
- **Which tripwire:** presentation tripwire (second hit same day) + structural gap (no home for live defects).
- **Root cause:** board file set had no bugs.md; presentation used process jargon ("debt") and one-word statuses instead of Built / Checked-live / Deviations / Owed columns in kitchen English.
- **Patch applied to SKILL.md:** `bugs.md` added as a sixth board file (+ template) with a verified-fixed-only close rule; `status` output gains a 🐛 bugs line and "debt" renders as "still owed"; adopt step 4 routes live defects to bugs.md. Presentation rule: owner-facing views use plain kitchen words and show per-phase Built / Checked-in-real-use / Deviations columns.

## 2026-07-06 — No logic-level check between "built" and "walked live" (Divya: fields must OBEY their meaning)
- **What happened:** Divya asked how the system catches a field that's stored but never obeyed (B1's root: available-from saved since January, enforced never) when nobody walks it live. The skill's verification had only two nets — promise reconcile and live walks — with nothing that REASONS about what each built piece implies.
- **Which tripwire:** structural gap (a whole verification class missing), surfaced by the owner, not a run.
- **Root cause:** reconcile was promise-driven; a promise list can be complete while a field's implications are silently dropped. Storage ≠ behavior was never stated as a rule.
- **Patch applied to SKILL.md:** new § "The meaning contract" — every touched field/setting/control gets its implications enumerated, each traced to an enforcing line + test; the reconciler re-derives the table independently and walks the diff field-by-field. Dispatch template gains the matching BLOCKING plan step. Runs by pure reasoning — no human, no live environment needed.

## 2026-07-06 — Near-duplicate board: started `adopt hq` while `modules/headquarters/` already existed (built same day by a parallel lane)
- **What happened:** Divya asked for "all HQ work in one plan"; I launched a full adopt intake (3 sweepers) for slug "hq" without first checking `docs/superpowers/modules/` — where a complete `headquarters` board (24 phases, debt, bugs, whole-module plan) had been created hours earlier by another session. The docs sweeper caught it; a duplicate board was one synthesis step away.
- **Which tripwire:** structural gap — adopt had no existing-board check; slug variance (hq vs headquarters) defeated any implicit check.
- **Root cause:** resume-ritual step 0 only covers the missing-board case; adopt (the board-creating command) never checked the inverse. No slug convention.
- **Patch applied to SKILL.md:** adopt gains BLOCKING step 0 — list modules/, check name variants, resume-don't-duplicate. (Sweep cost not wasted: the intake evidence feeds the EXISTING board instead.)

## 2026-07-06 — PR #2213 merged to dev un-reconciled, despite "Do NOT merge" in the dispatch prompt
- **What happened:** Phase 12's build PR merged 39 min after opening, under Divya's credentials (agent or human — pending her confirm), with the reconcile never run AND the Gemini auto-review down on quota. Zero independent eyes at merge time.
- **Which tripwire:** rail breach (dispatch prompt instruction ignored) + design gap (reconcile had no trigger tied to the PR; it waited for a Conductor invocation that came late).
- **Root cause:** "Do NOT merge" was one quiet line, not a named stop-trigger; agents carry merge-capable credentials; reconcile sequencing said "when the PR lands" instead of "on the OPEN PR, pre-merge."
- **Patch applied:** dispatch template now makes merging a STOP-TRIGGER VIOLATION in bold (credentials ≠ permission; only Divya by name in-window may authorize); SKILL.md run step 4 now reads "reconcile runs ON THE OPEN PR — merge only after the report card." Safety fact preserved: an early merge cannot close the phase; it only gets logged. GitHub-level hard lock (branch protection on dev) offered to Divya/Zaid as the physical enforcement option.

## 2026-07-08 — Reconcile ruled #2227 "CLEAN (mergeable)" while its Vercel type-check was RED
- **What happened:** Phase 12 A.1 (PR #2227) failed the Vercel PR build's TypeScript type-check the day it opened (07-07). The 07-06 fresh-eyes reconcile ruled it "CLEAN (mergeable)" — its evidence was vitest runs + preview DB probes only. vitest (esbuild) does NOT type-check, and the reconciler never looked at the PR's CI/Vercel gate. The board carried "clean, mergeable" for two days until a `run` sweep checked `gh pr checks 2227` and found the red build.
- **Which tripwire:** #1 — "a phase turned out half-done AFTER its card said ✅ / clean" → reconcile evidence bar too low. Also board-vs-reality gap (status would have answered wrong).
- **Root cause:** the reconcile evidence menu (test run / screenshot / walked flow / preview probe) omitted the one gate CLAUDE.md names as authoritative for the type-narrowing class — the Vercel PR build. A green vitest + preview probe is NOT the same as a green build; "mergeable" was asserted without reading the merge gate.
- **Patch applied to SKILL.md:** the reconcile § now BLOCKS ruling any PR "clean / mergeable" without first reading its CI status (`gh pr checks <PR>` / `gh pr view --json statusCheckRollup`) and confirming the Vercel build is green — a red or missing build gate is an automatic ❌ regardless of local test results, because vitest/tsc-noEmit miss the type-narrowing class the full build catches. Resume-ritual "phantom dones" step widened to also flag any 🔎/awaiting-merge card whose PR CI is red.

## 2026-07-11 — Reported dashboard coordinates to cards that didn't exist on the dashboard
- **What happened:** Practical-test design session annotated HQ phases 19/22/23 on the HQ scoreboard's phase TABLE and told Divya "on your dashboard: HQ → cards 22/23". Those phases had no card files under `phases/` — and the Conductor Dashboard renders ONLY card files (verified live: `/api/modules/headquarters` served exactly the 14 existing cards). Divya went looking and could see none of them ("I can't see any of them"). The checklists card 19 DID exist and was served — she just needed a refresh — but the HQ pointers were to nothing.
- **Which tripwire:** the presentation-gap tripwire — "Divya was asked to decide on / look at something she couldn't see."
- **Root cause:** the "dashboard coordinates" rule assumed anything written to a board is visible on the dashboard. False: scoreboard-row annotations without a card file are invisible to her. The coordinate was minted from the board's internal state, not from what the dashboard actually renders.
- **Patch applied to SKILL.md:** dashboard coordinates may only point at things that exist as CARD files (the dashboard renders `phases/*.md`, not scoreboard rows). Before citing a coordinate, ensure the card exists — mint a skeleton card (promises P-PENDING + the decided facts in plain language) for any phase Divya must see before its plan is written.

## 2026-07-11 — Changed Divya's dashboard unasked instead of fixing the report language
- **What happened:** Divya said "the cards do not have any number and the promises do not have any number — when you tell me card 19 promise 6, I have no idea what it is." The correct reading: her board is deliberately code-free (her own calm-board slice, same day), so reports must speak in NAMES. Instead, the Conductor "fixed" her dashboard — un-hid `.t-no`/`.p-id` permanently, edited the toggle label, committed it — without being asked. She rejected it flat: "I did not ask you to change the dashboard... Revert back to what it was." Reverted (fc26780), verified live.
- **Which tripwire:** none existing — this is the user-control rule from the global CLAUDE.md ("agree the plan up front", "still stop for the divergent"): a complaint about MY output was treated as a mandate to change HER tool.
- **Root cause:** the SKILL's coordinate convention was written in numbers ("card <N> → P<n>") while her dashboard renders names-only by design. When the convention collided with her screen, the session changed the screen to match the convention instead of the convention to match the screen. Backwards: her surface is the contract; my language adapts.
- **Patch applied to SKILL.md:** the dashboard-coordinates rule is now NAMES-FIRST — `<Board> → the "<card NAME>" card → the "<promise's plain words>" promise`, numbers/PR ids only in a trailing "(for the team: …)" parenthetical. Explicit ban added: never re-show codes on her dashboard; fix the language, never her tool.
