---
description: Is my divya-kit live on THIS project? Lists every skill/agent/command it provides and confirms the rulebook loaded.
---

The user wants a plain-English confirmation that the **divya-kit** plugin is fully
loaded and working on the project this session is currently in — the "is my staff
handbook actually in this kitchen?" check. Run it on whatever project they're in; the
kit is meant to work on ALL of them, not one.

Do this, then report:

## 1. Where am I, and local or cloud?
- Cloud vs local: the folder `/Users/ddpda/Local/auntyskitchen` exists ONLY on Divya's
  Mac. If it's absent, this is a cloud session (web/desktop-cloud).
- Which project: prefer the `CLAUDE_PROJECT_DIR` env var; else `git rev-parse
  --show-toplevel`. Report the project folder name in plain English.

## 2. Inventory — what the kit provides here (read from disk, the source of truth)
Use `$CLAUDE_PLUGIN_ROOT` (the plugin's own root) to count and list:
- **Skills** — every `skills/*/SKILL.md` (report the count and the folder names).
- **Agents** — every `agents/*.md` (report the count and each agent's name).
- **Commands** — every `commands/*.md` (report the names).
Keep it to tidy bullet lists, not walls of text.

## 3. Is it actually LIVE in this session (not just present on disk)?
- **Rulebook:** confirm Divya's working-style rules are active in your context right now
  (the `<EXTREMELY_IMPORTANT>` block the SessionStart hook injects, or the
  `divya-working-style` skill). If you can see those house rules, say so — that's the
  proof the SessionStart hook fired on this project.
- **Skills/agents visible:** confirm the kit's skills and agents appear in the session's
  available list (they should, if the plugin loaded). Note any that are present on disk
  but NOT showing up as loaded — that's the one real failure mode (usually a malformed
  frontmatter or an over-long description), and it's worth flagging by name.

## 4. Verdict — one clear line
Give Divya a single plain-English bottom line, e.g.:
- ✅ **"Your kit is live here — 16 skills, 12 agents, 4 commands, and the rulebook all
  loaded on <project>."** (fill in the real numbers you found), or
- ⚠️ a specific, plain-English flag if something's present on disk but not loading, with
  the likely cause and the fix.

Rules for the reply:
- Plain English, jargon-free, brief labelled bullets — no essays, no code syntax dumps.
- This is a read-only status check: make NO edits, NO commits, NO changes of any kind.
- If the verdict is all-green, keep it short and celebratory; only go long if something's
  actually wrong.
- If something IS wrong, do NOT point at claude.ai → Settings → Plugins — there is no
  user-scope plugin switch there, and the plugin route as a whole is dead in the cloud
  (a trust gate stops project-enabled external plugins from auto-installing). The kit
  loads via the **bootstrap hooks** in `.claude/settings.json` (copied from the kit's
  `bootstrap/project-settings.json`), which link the kit into the session under BARE
  names (`/kit-check`, no `divya-kit:` prefix). Check, in order:
  1. The settings file with the bootstrap hooks is committed on the branch the session
     cloned (`.claude/settings.json`, SessionStart hook present).
  2. The kit actually arrived: does `~/.divya-kit/skills/` exist, and does the project's
     `.claude/skills/` contain symlinks? If not, the clone failed — the kit repo is
     private, so a session on any OTHER repo needs either a `DIVYA_KIT_TOKEN` env var in
     the cloud environment, the kit repo added as a second source, or the kit repo made
     public.
  3. The cloud environment's network access allows GitHub — "None" silently kills the
     clone.
  4. Hooks fired at all: some session types may not run SessionStart hooks — check
     whether the rulebook (`<EXTREMELY_IMPORTANT>` block) is in context.
