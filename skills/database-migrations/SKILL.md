---
name: database-migrations
description: Use BEFORE writing any database migration, schema change, or DDL — new table, column, index, constraint, RLS policy, database function, trigger, or view. Also when verifying whether a migration actually landed in a database, when a "table/column doesn't exist" error appears in production, when reconciling preview vs production schema drift, or when the user asks "did that migration get applied?" / "is the migration owed?". Triggered by /database-migrations. Rigid — follow it exactly.
---

# Database Migrations — the rigid protocol

## Why this skill exists

A migration is the only kind of change in this system that can take **production** down for **every restaurant at once**, silently, with a green deploy and no error in the logs. Application code fails loudly; a missing column fails as a 500 on an endpoint that three other features happen to share.

And there is a second, quieter failure that has cost more time than any outage: **the migration file exists in the repo, but the table does not exist in the database.** "OWED migration" is the most repeated debt in this project's history. It is not carelessness — it is a missing pipe, and this skill is the plug.

**This skill is RIGID.** Do not adapt away its steps. Do not decide a step is unnecessary for "a small column add" — the small column adds are the ones that break things.

---

## Ground truth: how migrations ACTUALLY reach each database

Verified 2026-07-11. If any of this changes, fix it here first.

| Database | Project id | How a migration lands | Who does it |
|---|---|---|---|
| **Preview** (safe) | `oqgwailwxsmffaljubdy` | **Nothing automatic exists.** Applied by hand in the Supabase dashboard SQL editor. | **A human. Every time.** |
| **Production** (live) | `onfwarkuhytfzlzccbyx` | CI workflow `production.yml` runs `supabase db push --include-all` on every push to `main`. | Automatic on merge |

**Two consequences you must design around:**

1. **Preview is manual, so preview is always the one that gets forgotten.** A migration that only exists as a file is not applied. Never assume. Always verify (step 2 below).

2. **On merge to `main`, the migration and the code race each other.** Vercel deploys the code and CI pushes the migration at the same time, and nothing guarantees the migration wins. So: **write every migration to be applied safely BEFORE its code**, and write every consuming query to survive the migration not being there yet (see step 6).

There is **no Supabase CLI on this machine.** You cannot run `supabase db push` locally. Do not write instructions that assume you can.

---

## Your one route to the database: two read-only MCP servers

You reach both databases through MCP. Load the tools with `ToolSearch` (query: `supabase`), then use them.

| Server | Database | What it is |
|---|---|---|
| `supabase-preview` | Preview `oqgwailwxsmffaljubdy` | The safe copy. Look here freely. |
| `supabase-production` | Production `onfwarkuhytfzlzccbyx` | **Live restaurants.** Look, never touch. |

Useful tools: `execute_sql` (runs SELECT and `information_schema` inspection), `list_tables`, `list_migrations`, `list_extensions`.

### The lock is real — and you must still behave as if it weren't

Both servers run `read_only=true`, which connects as a **read-only Postgres user**. The database itself rejects any write. `apply_migration` and the other mutating tools **do not exist** on these servers — they are not merely discouraged.

So you cannot damage anything through MCP. Good. But:

- **Never go looking for another way in.** Do not reach for the service-role key, a direct Postgres connection, the Supabase CLI, or the Management API to work around the read-only lock. The lock is the owner's decision, not an obstacle to route around. **If a task genuinely cannot be done read-only, say so and stop** — that is the correct outcome, not a problem to solve.
- **Applying a migration is a HUMAN action.** You write the SQL; a person runs it. See step 7.
- **No PII in anything you report.** Names, emails, phone numbers, PINs — never quoted back. Refer to rows by id or by shape.

**If the MCP servers aren't connected** (not authorised, or erroring): say so out loud — *"I cannot see the database; everything below is unverified"* — and **do not pretend otherwise.** A migration written blind is a guess, and guessing is allowed only when you announce that you are guessing.

### A bounded check, not an endless search (added 2026-07-12)

In a **dispatched sub-agent session**, these tools have repeatedly been genuinely absent — not misnamed, not mis-queried, actually not propagated to the sub-agent's tool surface. Do not burn turns rewording `ToolSearch` queries hoping one phrasing unlocks them. One bounded check is enough:

1. `ToolSearch` with query `"supabase"`.
2. `ToolSearch` with query `"select:mcp__supabase-preview__execute_sql,mcp__supabase-production__execute_sql"`.
3. If both return nothing, try direct invocation once (e.g. call `mcp__supabase-preview__execute_sql` directly) to see the actual error.

If all three fail, **stop immediately** — do not keep trying synonyms — and report the servers unreachable in this session, per the paragraph above.

**The "MCP Server Instructions" block that appears in context (usage guidelines for `supabase-preview`/`supabase-production`) is static server metadata, injected whenever the server is *configured* — it is NOT evidence the tools are actually callable in this session.** Seeing that block is not a reason to assume the tools will work; only a successful tool call is.

---

## The protocol

### Step 1 — Never trust the plan's description of the schema

The plan says "add `swap_status` to `shifts`." The plan is not evidence. Another agent may have added it yesterday in a migration you haven't pulled.

### Step 2 — Look, before you write a single line of SQL

Run these against **both** databases. The answers are frequently different — production runs behind preview.

```sql
-- Does the column exist?
SELECT column_name, data_type, is_nullable FROM information_schema.columns
WHERE table_name = 'your_table' AND column_name = 'your_column';

-- Does the table exist?
SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename = 'your_table';

-- Does the function exist?
SELECT proname FROM pg_proc WHERE proname = 'your_function';

-- Does the constraint / index exist?
SELECT conname FROM pg_constraint WHERE conname = 'your_constraint';
SELECT indexname FROM pg_indexes WHERE indexname = 'your_index';

-- Is RLS on, and what policies exist?
SELECT relname, relrowsecurity FROM pg_class WHERE relname = 'your_table';
SELECT policyname, cmd, qual FROM pg_policies WHERE tablename = 'your_table';

-- Which migrations has this database actually seen?
SELECT version FROM supabase_migrations.schema_migrations ORDER BY version DESC LIMIT 10;
```

**Report what you found before you write anything.** If the thing already exists, say so and stop — the migration may not be needed at all.

### Step 3 — Claim a timestamp that cannot collide

```bash
date +%Y%m%d%H%M%S              # generate it live — right now
ls supabase/migrations/<that>*  # confirm it's free
```

Filename: `supabase/migrations/YYYYMMDDHHMMSS_description.sql`

- **14 digits, NO underscore inside the timestamp.** The Supabase CLI treats everything before the *first* underscore as the version. `20260711_143022_add_thing.sql` becomes version `20260711` — which collides with every other migration made that day, and breaks the production deploy.
- **Never copy a timestamp** from an existing file.
- **Never invent a round one** (`20260401000000`). Round numbers collide; real clock times don't.

### Step 4 — Write SQL that is safe to run twice

Every statement idempotent. Assume it will be re-run, out of order, on a database in an unknown state — because it will be.

- `CREATE TABLE IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS`, `CREATE OR REPLACE FUNCTION`, `CREATE INDEX IF NOT EXISTS`
- `DROP ... IF EXISTS` before re-creating
- Never `DROP COLUMN` / `DROP TABLE` without `IF EXISTS`
- Never assume a column's type — `ALTER COLUMN ... TYPE ... USING` with an explicit cast

**Every new table, without exception:**
```sql
ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;
```
- A `restaurant_id` column with a foreign key **and an index** (unless it's a pure lookup table)
- **Every** policy includes `OR is_platform_admin()` — otherwise impersonation breaks
- **INSERT policies validate `restaurant_id` against the caller's restaurant** — not merely `profile_id = auth.uid()`. A user inserting a row tagged with *someone else's* restaurant id is the classic hole.
- Any `SECURITY DEFINER` function **must** pin `SET search_path` — an unpinned one is privilege escalation.

**Every migration that adds a table, column, or foreign key ends with:**
```sql
NOTIFY pgrst, 'reload schema';
```
Without it, PostgREST keeps serving the old schema. The DDL succeeds, and every query against the new thing still fails. This has bitten this project repeatedly.

Write the matching rollback file. If you can't say how to undo it, you don't understand it yet.

### Step 5 — Stop before anything destructive

`DROP`, `TRUNCATE`, a type change that loses data, a `NOT NULL` on a column with existing nulls: **stop.** Explain the risk in plain English — *"this would permanently delete the notes people have already written"* — and wait for an explicit yes. Never infer permission.

### Step 6 — Make the consuming code survive the race

Because the migration and the code go live together on the merge to `main`, **write the code to degrade, not to explode**:

Instead of one query that joins through the new relationship (which 500s the whole endpoint if the migration is late), fetch the main row first, then fetch the new data in a separate `try/catch`. The feature loses its new bit; it does not take down the page and the three other features sharing that endpoint.

### Step 7 — Paste the full SQL into the chat. Always. No exceptions.

**BLOCKING.** The owner often cannot open files from her environment. A file path or a link **alone is never enough**.

Paste the **complete** contents of the `.sql` file directly into your message, inside a fenced ` ```sql ` block she can copy in one go. The SQL comes **first**; a clickable markdown link to the file is a nice extra, never a substitute.

Then say, in plain English:
- **Which databases** it must be applied to (preview? production? both?)
- **That preview is manual** — she (or someone) must paste it into the Supabase dashboard SQL editor, because nothing does it automatically
- **That production happens by itself** when the work merges to `main`
- **That it must land before the new code goes live**
- **Whether it's safe to re-run** (it should be)
- **An offer to walk her through it**

### Step 8 — Verify it actually landed. Do not assume.

After it's been applied, prove it:
```sql
SELECT version FROM supabase_migrations.schema_migrations WHERE version = 'YYYYMMDDHHMMSS';
```
And then confirm the *thing itself* exists — the column, the policy, the function — using the step-2 queries. A row in the migrations table only means the file ran; check that it did what it claimed.

**"Merged" is not "applied." "Applied to production" is not "applied to preview."** State exactly where it has landed and where it has not. A migration that is applied to only one of the two databases is **still owed**, and must be reported as owed, not as done.

---

## The checks you can run today

```bash
npm run test:db         # database tests
npm run db:check-sync   # preview-vs-production drift — needs a SUPABASE_ACCESS_TOKEN, which
                        # is deliberately NOT set on this machine. Use the MCP servers instead:
                        # run list_migrations against supabase-preview and supabase-production
                        # and compare. Same answer, no writable credential lying around.
```

A weekly CI job (`schema-drift.yml`) also compares the two. If it's shouting, believe it.

---

## What "done" means

A migration is **not** done when the file is written. It is not done when the PR merges. It is done when:

1. The SQL was pasted in chat, in full. ✅
2. Both databases have been **checked** (step 8) and you can name, for each, whether it is applied. ✅
3. The consuming code survives the migration not being there yet. ✅
4. The rollback file exists. ✅

Anything short of that gets reported as **owed**, in plain English, with what remains.

---

## Self-improvement loop (mandatory)

If this skill misses — a migration collides, a schema check was skipped, a column didn't exist, a database was silently left behind, PostgREST served stale schema, a destructive statement ran without sign-off — **log it in `failures.md` next to this file and patch this SKILL.md in the same session.** A miss that isn't written down happens again.
