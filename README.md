# claude-code-personal

Divya's personal Claude Code kit, packaged as a plugin so it travels to the **web and
desktop apps** — not just the local CLI. The kit's *contents* live only here; a project
repo needs just a tiny 6-line pointer file to load it in the cloud (see
[Enable it](#enable-it)), never a copy of the kit itself.

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

## Enable it

Enabling is **two separate jobs** — the local CLI and the web/cloud work differently.
There is **no single account-level switch** that turns the kit on everywhere; a plugin
you enable only in your user settings does **not** reach cloud sessions
([docs](https://code.claude.com/docs/en/claude-code-on-the-web)).

### Local CLI (your Mac) — once

```bash
# Registers the marketplace and installs the kit at user scope
/plugin marketplace add divyap-01/claude-code-personal
/plugin install divya-kit@divya-personal
```

That's all the local CLI needs — the kit loads in every local session from then on.

### Web / desktop-cloud — per project repo

A cloud session is a **fresh clone of one repo**; nothing from `~/.claude/` travels with
it. To make the kit load in a repo's cloud sessions, commit this tiny **pointer file** to
that repo — `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "divya-personal": {
      "source": { "source": "github", "repo": "divyap-01/claude-code-personal" }
    }
  },
  "enabledPlugins": {
    "divya-kit@divya-personal": true
  }
}
```

- It's **not** the kit — just an address label that tells a fresh session to fetch the
  kit from GitHub and switch it on. The kit stays in this one repo.
- Requires the repo's cloud environment to allow **network access to GitHub** (it fetches
  the marketplace at session start).
- **Per repo:** every project you want the kit on gets this file, once. There is no global
  path — that's the documented trade-off, not a missing setting.
- This repo already carries the file (dogfood): open a fresh cloud session on it and run
  `/kit-check` or `/debugging-protocol` to confirm the kit loaded.

> Heads-up: enabling the plugin in a repo also switches on its **gates** (PR / freeze /
> box) for that repo's sessions. That's intended for product repos; if you ever want a
> repo to carry the skills/agents but not the walls, drop the hooks from a repo-local copy.

## Bypasses (unchanged, cloud-aware)

`touch ~/.claude/.allow-ungated-pr` / `.allow-main-checkout` / `.allow-frozen-branch` /
`.allow-long-run` / `.allow-prod-migration` — visible, reversible, and yours to grant.
