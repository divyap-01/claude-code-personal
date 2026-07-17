# claude-code-personal

Divya's personal Claude Code kit, packaged so it travels to the **web and desktop apps**
— not just the local CLI. The kit's *contents* live only here; a project repo needs just
one small settings file to load it in the cloud (see [Enable it](#enable-it)), never a
copy of the kit itself.

Locally, nothing changes: her `~/.claude/` setup keeps running exactly as before, and
the cloud bootstrap stays silent on her Mac so the two never collide. In the **cloud**
(web / desktop-cloud), where `~/.claude/` doesn't exist, the bootstrap supplies the same
agents, rulebook, and safety gates.

## What's inside

| Folder | What it is |
|---|---|
| `agents/` | The 12 agents of the org — planner, builder, pr-shipper, migration-steward, security-auditor, verifier, debugger, smoke-tester, designer, screen-inspector, repo-steward, explainer. |
| `skills/divya-working-style/` | The global working-style rulebook (her `~/.claude/CLAUDE.md`). Auto-injected at session start in the cloud. |
| `commands/` | `/aside`, `/brainstorm`, `/write-plan`, `/execute-plan`, `/kit-check`. |
| `reference/` | Docs the rulebook and agents cross-reference — cost doctrine, design rules, agent failures log. |
| `hooks/` | The safety gates (`agent-guard.py`), the box-gate clock (`job-clock.py`), and the rulebook injector (`inject-rules`). |
| `bootstrap/` | The cloud loader — `link-kit.sh` plus the `project-settings.json` file each project repo commits. |

## The gates — local vs cloud

The safety walls are **logic**, not machine tricks, so almost all of them work in the
cloud. The only difference is where the project lives, which the guard now works out on
its own instead of assuming a fixed folder.

| Gate | Local (your Mac) | Cloud (web/desktop) |
|---|---|---|
| PR gate (no un-reviewed PR) | ✅ (via `~/.claude/hooks`) | ✅ |
| Freeze gate (shipped branch is closed) | ✅ | ✅ |
| Box gate (stop after 2 idle hrs) | ✅ | ✅ |
| Promote gate (owed migrations block main) | ✅ | ✅ if the owed-list is present |
| Prod-DB gate (no writes to production) | ✅ | ✅ |
| Migration-name gate | ✅ | ✅ |
| Worktree gate (main-checkout lock) | ✅ | ⏸️ relaxed — each cloud session gets its own clone, so the hazard can't occur |
| Local housekeeping sweeps | ✅ | — (nothing to sweep in the cloud) |

Locally every cloud hook exits immediately (the standalone `~/.claude/hooks` already do
the work); they only activate in the cloud.

## Enable it

Enabling is **two separate jobs** — the local CLI and the web/cloud work differently.

### Local CLI (your Mac)

Nothing to do — the standalone `~/.claude/` setup (rulebook, hooks, commands) keeps
working exactly as before. The cloud bootstrap detects the Mac and stays out of the way.

### Web / desktop-cloud — per project repo

> **Why not a plugin?** The kit used to load via `enabledPlugins` +
> `extraKnownMarketplaces` in a pointer file. That path is dead in the cloud: a trust
> gate stops externally-sourced, project-enabled plugins from ever auto-installing at
> session start (verified live, July 2026), and account-level plugin installs don't reach
> cloud sessions either. The bootstrap below is the route that actually works — and it
> loads everything under **bare names** (`/kit-check`), with no `divya-kit:` prefix.

A cloud session is a **fresh clone of one repo**; nothing from `~/.claude/` travels with
it. To make the kit load in a repo's cloud sessions, copy this repo's
[`bootstrap/project-settings.json`](bootstrap/project-settings.json) into that repo as
`.claude/settings.json`, commit it, and you're done. At session start its hooks:

1. **Find the kit** — a sibling checkout if the session has one, else a cached copy under
   `~/.divya-kit`, else a fresh shallow clone of this repo.
2. **Link** the kit's skills, agents, and commands into the session's `.claude/`
   (session-local symlinks — `git status` in the project stays clean, nothing gets
   committed).
3. **Inject the rulebook** and wire the gates (PR / freeze / box / prod-DB).

Requirements and caveats:

- The repo's cloud environment must allow **network access to GitHub**.
- **While this repo is private**, a session on *another* repo can't clone it anonymously.
  Pick one: make this repo public; or create a fine-grained read-only GitHub token for
  this one repo and set it as a `DIVYA_KIT_TOKEN` environment variable in each cloud
  environment (the bootstrap uses it automatically); or add this repo as a second source
  on the session so the sibling-checkout path kicks in. Sessions **on this repo itself**
  need none of that.
- **Per repo:** every project you want the kit on gets the one settings file, once.
- This repo dogfoods the same mechanism (`.claude/` symlinks + the same settings file):
  open a fresh cloud session here and type `/kit` — `/kit-check` should autocomplete.

> Heads-up: committing the settings file also switches on the kit's **gates** (PR /
> freeze / box) for that repo's sessions. That's intended for product repos; if you ever
> want a repo to carry the skills/agents but not the walls, delete the `PreToolUse` and
> `UserPromptSubmit` blocks from your copy of the file.

## Bypasses (unchanged, cloud-aware)

`touch ~/.claude/.allow-ungated-pr` / `.allow-main-checkout` / `.allow-frozen-branch` /
`.allow-long-run` / `.allow-prod-migration` — visible, reversible, and yours to grant.
