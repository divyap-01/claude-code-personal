# database-migrations — failure log

Every miss gets logged here and patched into `SKILL.md` **the same session**. A miss that isn't written down happens again.

Format: date · what went wrong · what it cost · what was patched into the skill.

---

## Seeded from real history (pre-dating the skill)

These are the failures the skill was built to prevent. They are logged so the skill never quietly loses the lesson.

**2026-05-06 — Timestamp truncation collided every migration made that day.**
A file named `YYYYMMDD_HHMMSS_*` (underscore *inside* the timestamp) was parsed by the Supabase CLI as version `YYYYMMDD` — the CLI splits on the first underscore. It collided with every other migration created that day and broke the deploy.
→ Patched: Step 3 — 14 digits, no internal underscore, generated live, checked for collision.

**Recurring — "OWED preview/production migration."**
The single most repeated debt in this project's memory. A migration file lands in the repo; the database never gets it. Root cause is not carelessness: **preview has no automatic apply path at all**, so it depends entirely on a human remembering.
→ Patched: Ground-truth table (preview is manual, production is automatic on merge to `main`). Step 8 — "merged" is not "applied"; state per-database status explicitly, and report a half-applied migration as **owed**.

**Recurring — PostgREST served a stale schema.**
The DDL succeeded, the column existed, and every query against it still failed. PostgREST caches the schema and will not notice a new table/column/FK until told.
→ Patched: Step 4 — every migration adding a table, column, or FK ends with `NOTIFY pgrst, 'reload schema';`

**Recurring — code deployed before its migration.**
Vercel ships the code the instant the branch merges; the migration races it. Code that queries a not-yet-existing table 500s the endpoint — and takes down the other features sharing it.
→ Patched: Step 6 — write consuming code to degrade (fetch the main row, then the new data in a separate try/catch), never to explode.

**Recurring — the migration was written against a schema that didn't exist.**
A plan described a column; the agent believed the plan; the column wasn't there. Mocked tests passed, production 500'd.
→ Patched: Steps 1–2 — the plan is not evidence. Query `information_schema` on **both** databases before writing a line of SQL, and report what you found first.

---

## New failures

<!-- Append below. Date · what happened · cost · what was patched. -->

**2026-07-12 — supabase-preview / supabase-production MCP tools genuinely unreachable in a dispatched (sub-agent) session, for at least the third time in a row.**
Two prior agents reported they "could not find" the read-only DB tools; a dispatch brief insisted they were there and told the third agent to try harder (`ToolSearch` with specific query strings, then `select:mcp__supabase-production__execute_sql,mcp__supabase-preview__execute_sql`). None of it worked: `ToolSearch` returned "No matching deferred tools found" for every phrasing tried (`supabase`, `supabase execute_sql`, `execute sql query database`, `list_tables preview production`, `mcp__supabase-preview__execute_sql`, `postgres query rows table`, `information_schema columns table`, `get_advisors list_migrations get_logs project`), and direct invocation of `mcp__supabase-preview__execute_sql` / `mcp__supabase-preview__list_tables` both errored `No such tool available`. The MCP servers' *instruction blocks* (usage guidelines for supabase-preview/production) appeared in context regardless — that block is static server metadata and is NOT evidence the tools are actually callable in this session. Likely cause: these MCP servers are configured for the top-level session but not propagated into a dispatched sub-agent's tool surface. Cost: a full round of exhaustive re-searching before concluding, again, that the tools are absent — the skill's own advice ("say so, don't pretend") was right, but nothing told the agent how *much* searching is enough before giving up and reporting.
→ Patched: added a "quick, bounded check" note under "Your one route to the database" — try at most 2 `ToolSearch` queries (`"supabase"` and `"select:mcp__supabase-preview__execute_sql,mcp__supabase-production__execute_sql"`) plus one direct invocation attempt; if all three fail, stop searching immediately and report the servers unreachable rather than burning further turns on query rewording. Also noted explicitly that the "MCP Server Instructions" context block is NOT proof of tool availability.
