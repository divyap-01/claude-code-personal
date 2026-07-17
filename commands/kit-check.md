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
- If something IS wrong, remember the fix might be an account-setting (enable divya-kit at
  **User** scope in claude.ai → Settings → Plugins) rather than a code change — say so.
