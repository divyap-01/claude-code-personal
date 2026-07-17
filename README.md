# claude-code-personal

Divya's personal Claude Code kit, packaged as a plugin so it travels to the **web and
desktop apps** — not just the local CLI. None of this needs to live in any project repo
(Aunty's Kitchen stays untouched).

Locally, nothing changes: her `~/.claude/` setup keeps running exactly as before, and
this plugin stays silent so the two never collide. In the **cloud** (web / desktop-cloud),
where `~/.claude/` doesn't exist, this plugin supplies the same agents, rulebook, and
safety gates.

## What's inside

| Folder | What it is |
|---|---|
| `agents/` | The 12 agents of the org — planner, builder, pr-shipper, migration-steward, security-auditor, verifier, debugger, smoke-tester, designer, screen-inspector, repo-steward, explainer. |
| `skills/divya-working-style/` | The global working-style rulebook (her `~/.claude/CLAUDE.md`). Auto-injected at session start in the cloud. |
| `commands/` | `/aside`, `/brainstorm`, `/write-plan`, `/execute-plan`. |
| `reference/` | Docs the rulebook and agents cross-reference — cost doctrine, design rules, agent failures log. |
| `hooks/` | The safety gates (`agent-guard.py`), the box-gate clock (`job-clock.py`), and the rulebook injector (`inject-rules`). |

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

Locally the plugin's `agent-guard.py` exits immediately (the standalone
`~/.claude/hooks/agent-guard.py` already does the work); it only activates in the cloud.

## Enable it (once)

```bash
# In the local CLI — this registers the marketplace on your account
/plugin marketplace add divyap-01/claude-code-personal
/plugin install divya-kit@divya-personal
```

Then confirm it's enabled for the web/desktop surfaces in the claude.ai Plugins panel
(User scope). Once enabled on your account, it loads in **every** web session, whatever
project you open.

## Bypasses (unchanged, cloud-aware)

`touch ~/.claude/.allow-ungated-pr` / `.allow-main-checkout` / `.allow-frozen-branch` /
`.allow-long-run` / `.allow-prod-migration` — visible, reversible, and yours to grant.
