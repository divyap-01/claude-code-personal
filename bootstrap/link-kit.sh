#!/bin/sh
# Materialise divya-kit into the current project's .claude/ so cloud sessions load
# everything under bare names (no plugin machinery, no divya-kit: namespace prefix).
#
# Idempotent, silent on stdout (SessionStart stdout is reserved for hook JSON).
# No-ops on Divya's Mac, where the standalone ~/.claude copies already provide the kit.

[ -d "/Users/ddpda/Local/auntyskitchen" ] && exit 0

KIT="${CLAUDE_PLUGIN_ROOT:-$HOME/.divya-kit}"
PROJ="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

[ -d "$KIT/skills" ] || exit 0

# The kit repo itself already carries .claude symlinks — nothing to link there.
KREAL=$(cd "$KIT" 2>/dev/null && pwd -P)
PREAL=$(cd "$PROJ" 2>/dev/null && pwd -P)
[ -n "$KREAL" ] && [ "$KREAL" = "$PREAL" ] && exit 0

mkdir -p "$PROJ/.claude/skills" "$PROJ/.claude/agents" "$PROJ/.claude/commands"

for d in "$KIT"/skills/*/; do
  [ -d "$d" ] || continue
  n=$(basename "$d")
  [ -e "$PROJ/.claude/skills/$n" ] || ln -s "${d%/}" "$PROJ/.claude/skills/$n"
done

for f in "$KIT"/agents/*.md; do
  [ -f "$f" ] || continue
  n=$(basename "$f")
  [ -e "$PROJ/.claude/agents/$n" ] || ln -s "$f" "$PROJ/.claude/agents/$n"
done

for f in "$KIT"/commands/*.md; do
  [ -f "$f" ] || continue
  n=$(basename "$f")
  [ -e "$PROJ/.claude/commands/$n" ] || ln -s "$f" "$PROJ/.claude/commands/$n"
done

# Keep the project's git status clean: the links are session-local, never committed.
# (info/exclude only hides UNTRACKED paths — the project's own tracked .claude files
# are unaffected.)
if [ -d "$PROJ/.git" ]; then
  EX="$PROJ/.git/info/exclude"
  grep -qs "divya-kit links" "$EX" || printf '# divya-kit links (session-local, never commit)\n.claude/skills/\n.claude/agents/\n.claude/commands/\n' >> "$EX"
fi

exit 0
