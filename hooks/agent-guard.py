#!/usr/bin/env python3
"""
Agent guard — the hard walls of the agent org.

  WALL 1 (PR gate)        no `gh pr create` without a fresh-eyes receipt for the exact
                          commit being shipped, plus a security verdict if the diff is
                          sensitive.
  WALL 2 (worktree gate)  no editing CODE in the main checkout — via the Edit/Write
                          tools OR the shell (sed -i, tee, redirects, git checkout/
                          merge). Docs and agent config are fine.
  WALL 3 (freeze gate)    once a branch has shipped its PR, it is CLOSED. A new finding
                          is a new PR. Set automatically by Wall 1 — nobody has to
                          remember to freeze.
  WALL 4 (box gate)       no dispatching agents more than BOX_HOURS after Divya last
                          spoke. Only a message from HER resets the clock.

Charters are instructions. These are walls. Exit code 2 blocks the tool call and the
message on stderr goes back to Claude, telling it exactly how to proceed.

--------------------------------------------------------------------------------------
WHY 3 AND 4 EXIST  (PR #2539, 2026-07-11 → 07-13: ~35 hours, ~55% of a weekly budget)

The fix itself took 48 minutes — commits 1–30. The other 70 commits were:
  · the SAME rule re-applied to a door nobody had looked for ("the third door", "the
    legacy door", "close every OTHER door", "guard the chokepoints, not each caller")
  · 22 security-audit rounds — not because the code was dangerous, but because the diff
    NEVER STOPPED MOVING. Every new fix invalidated the last audit.

That is what Wall 3 kills. Freeze the diff and the audit is run once.

Wall 4 exists because the agent org has quality gates but had no GOVERNOR. Agents never
tire and never say "this has gone on too long." Nothing anywhere said stop. So it ran
for 35 hours. The box is the stop.

The org's own hardest-won rule, from the code this very PR shipped:
    "A guard the caller must remember to call is a guard that will eventually not be
     called."
It is just as true of process as of code. Hence: walls, not good intentions.
--------------------------------------------------------------------------------------

Bypass (deliberate, visible, reversible — and TELL DIVYA you did it):
  touch ~/.claude/.allow-ungated-pr        disables Wall 1
  touch ~/.claude/.allow-main-checkout     disables Wall 2
  touch ~/.claude/.allow-frozen-branch     disables Wall 3  (Divya's "fold it in" override)
  touch ~/.claude/.allow-long-run          disables Wall 4  (unattended/cron runs)

--------------------------------------------------------------------------------------
CLOUD PORTABILITY  (this is the plugin copy, not the ~/.claude/hooks copy)

This file travels in the `claude-code-personal` plugin so the walls also stand in the
Claude Code CLOUD sandbox (web / desktop-cloud), where none of ~/.claude/ exists.

Two facts make that work with almost no change:
  · The gates are LOGIC, not machine state — a receipt, a freeze marker, a clock stamp.
    Their state lives under $HOME/.claude, which the cloud sandbox has too (fresh each
    session — which is exactly right: each cloud session earns its own receipts).
  · The ONLY machine-specific assumption was the hardcoded project path. It is now
    resolved dynamically (CLOUD branch below).

What changes in the cloud:
  · KEPT:  PR gate, freeze gate, box gate, promote gate, prod-DB gate, migration-name
           gate, lane-diary gate — all pure logic, all active.
  · RELAXED: the worktree gate (Wall 2). It exists ONLY because many LOCAL sessions
           share one checkout; each cloud session gets its own fresh clone, so the
           hazard cannot occur. Migration-filename discipline is still enforced.
  · SILENT LOCALLY: on Divya's Mac the standalone ~/.claude/hooks/agent-guard.py
           already runs these gates. This plugin copy exits immediately when it detects
           it is on her machine, so the two never double-fire.
--------------------------------------------------------------------------------------
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()

# The one fixed fact that tells local from cloud: this exact folder exists ONLY on
# Divya's Mac. In any cloud sandbox it is absent — no unreliable magic env var needed.
LOCAL_SHARED_CHECKOUT = Path("/Users/ddpda/Local/auntyskitchen")
CLOUD = not LOCAL_SHARED_CHECKOUT.exists()


def resolve_repo(cwd=None):
    """The repo this session is protecting.

    Local  → always the fixed shared checkout (behaviour unchanged from before).
    Cloud  → wherever Claude Code checked the project out this session: prefer the
             CLAUDE_PROJECT_DIR env var Claude Code sets, else the git top-level of
             the current working dir.
    """
    if not CLOUD:
        return LOCAL_SHARED_CHECKOUT
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and Path(env).is_dir():
        return Path(env).resolve()
    top = sh(["git", "rev-parse", "--show-toplevel"], cwd=cwd)
    if top:
        return Path(top).resolve()
    return LOCAL_SHARED_CHECKOUT


# Real value is set in main() once the session cwd is known; safe default until then.
REPO = LOCAL_SHARED_CHECKOUT
RECEIPTS = HOME / ".claude" / "pr-receipts"
FREEZE = HOME / ".claude" / "pr-freeze"
CLOCK = HOME / ".claude" / ".job-clock"

# How long may I keep spending on agents without Divya saying a word? (Wall 4)
BOX_HOURS = 2.0

# The tools that actually cost money. Wall 4 blocks these and ONLY these, so a box
# expiring can never strand a half-done merge, migration, or edit.
SPENDING_TOOLS = ("Agent", "Task", "Workflow")

# Files whose change means a human security verdict is required before shipping.
SENSITIVE = re.compile(
    r"(auth|login|logout|session|permission|role|rls|policy|pin\b|token|secret|"
    r"middleware|impersonat|kiosk|device|payroll|pay-?sheet|pay-?rate)",
    re.I,
)
# Any schema change is security-relevant: RLS, grants, definer functions live here.
SENSITIVE_DIRS = ("supabase/migrations/", "lib/auth/", "lib/supabase-server")

# Editable in the main checkout: docs and agent/tooling config. Never product code.
MAIN_CHECKOUT_ALLOWED = ("docs/", ".claude/", ".agents/", ".smoke-shots/")


def sh(args, cwd=None):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=15)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def block(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


def effective_dir(command, cwd, before=None):
    """Where will this command actually run? Honour the `cd <path>` nearest BEFORE the
    gated token — never a later one. A trailing cleanup (`… && gh pr create; cd /tmp`)
    used to make the gate evaluate /tmp and silently skip itself."""
    matches = list(re.finditer(r"cd\s+([^\s;&|]+)", command))
    if before is not None:
        matches = [m for m in matches if m.start() < before]
    if matches:
        p = Path(os.path.expanduser(matches[-1].group(1)))
        if p.is_dir():
            return p
    return Path(cwd) if cwd else Path.cwd()


# A git subcommand reached through global flags too: `git -C <path> push` and
# `git -c a=b commit` must gate exactly like `git push` / `git commit` — the org's own
# post-resume rule ("always git -C") walked straight through the bare-form regex.
def git_verb(verbs):
    return re.compile(r"\bgit\b(?:\s+-{1,2}\S+(?:\s+[^-\s]\S*)?)*\s+(" + verbs + r")\b")


GIT_COMMIT_PUSH = git_verb("commit|push")

# Every way a PR can be created, not just the polite one.
PR_CREATE = re.compile(
    r"\bgh\s+pr\s+create\b"
    r"|\bgh\s+api\b[^;|&]*/pulls\b"
    r"|\bcurl\b[^;|&]*api\.github\.com[^;|&]*/pulls\b"
)


# ------------------------------------------------------- TRIPWIRE: the promote gate
# Production is sometimes OWED migrations that must be applied before dev code reaches
# main, or whole features 500 in production. That obligation used to live only in
# prose on the board — "a guard the caller must remember to call is a guard that will
# eventually not be called." This file makes it machine-checked: one version per line,
# maintained by the lanes, cleared line-by-line as each lands in production.
OWED_MIGRATIONS = HOME / ".claude" / "owed-prod-migrations.txt"
PROMOTE = re.compile(
    r"\bgh\s+pr\s+create\b[^;|&]*--base[= ]+\"?main\b"
    r"|\bgit\b(?:\s+-{1,2}\S+(?:\s+[^-\s]\S*)?)*\s+push\b[^;|&]*\s(origin\s+main|\S+:main)\b"
)


def promote_gate(command, cwd):
    m = PROMOTE.search(command)
    if not m:
        return
    wd = effective_dir(command, cwd, before=m.start())
    common = sh(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=wd)
    if not common:
        return
    try:
        if not Path(common).resolve().is_relative_to(REPO.resolve()):
            return
    except (OSError, AttributeError):
        if str(REPO) not in common:
            return
    try:
        owed = [
            l.strip()
            for l in OWED_MIGRATIONS.read_text().splitlines()
            if l.strip() and not l.strip().startswith("#")
        ]
    except OSError:
        return  # no owed-list file — nothing recorded as owed
    if not owed:
        return
    listing = "\n".join(f"  · {v}" for v in owed)
    block(
        "🛑 PROMOTE GATE — blocked. Production is still OWED these migrations, and dev\n"
        "code must not reach main before they are applied (features 500 without them):\n\n"
        f"{listing}\n\n"
        "NEXT STEP: read the lane files on the board (they carry the required ORDER),\n"
        "apply each migration to production, verify each version exists in production's\n"
        "supabase_migrations.schema_migrations, then delete its line from\n"
        f"  {OWED_MIGRATIONS}\n"
        "When that file is empty this gate opens. Applying to production is Divya's\n"
        "call — never yours alone.\n"
    )


# ------------------------------------------------------- TRIPWIRE: the prod-DB gate
# The production Supabase MCP server is read-only at the server (read_only=true in the
# URL) — but that is one editable query-param away from not being true. This is the
# local backstop: migration-application and write-shaped SQL against PRODUCTION are
# blocked here regardless of what the server allows.
MCP_WRITE_SQL = re.compile(
    r"\b(insert|update|delete|alter|create|drop|truncate|grant|revoke)\b", re.I
)


def mcp_gate(tool, tool_input):
    if not tool.startswith("mcp__supabase-production__"):
        return
    if (HOME / ".claude" / ".allow-prod-migration").exists():
        return
    op = tool.rsplit("__", 1)[-1]
    if op == "apply_migration":
        block(
            "🛑 PROD DB GATE — blocked. Migrations are applied to PRODUCTION deliberately\n"
            "(Divya's call, in the lane's recorded order) — never casually from a session.\n\n"
            "If she has explicitly approved applying this migration to production:\n"
            "  touch ~/.claude/.allow-prod-migration   (tell her, and remove it after)\n"
        )
    if op == "execute_sql":
        q = str(tool_input.get("query", "") or "")
        if MCP_WRITE_SQL.search(q):
            block(
                "🛑 PROD DB GATE — blocked. That SQL would WRITE to the PRODUCTION database.\n"
                "Reads (SELECT) pass freely; writes to production go through Divya.\n\n"
                "If she has explicitly approved this write:\n"
                "  touch ~/.claude/.allow-prod-migration   (tell her, and remove it after)\n"
            )


# ---------------------------------------------------------------- WALL 1: the PR gate
def pr_gate(command, cwd):
    if (HOME / ".claude" / ".allow-ungated-pr").exists():
        return
    m = PR_CREATE.search(command)
    if not m:
        return

    wd = effective_dir(command, cwd, before=m.start())
    # Only guard THIS project. Other repos are none of our business.
    # --path-format=absolute matters: the bare form returns a path relative to `wd`,
    # which then resolves against the HOOK's cwd and silently disarms the gate.
    common = sh(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=wd
    )
    if not common:
        return
    try:
        in_this_repo = Path(common).resolve().is_relative_to(REPO.resolve())
    except (OSError, AttributeError):
        in_this_repo = str(REPO) in common
    if not in_this_repo:
        return

    sha = sh(["git", "rev-parse", "HEAD"], cwd=wd)
    if not sha:
        block(
            "🚧 PR GATE — I can't tell which commit you're shipping.\n\n"
            "Run the command with an explicit worktree, e.g.\n"
            "  cd /path/to/.worktrees/<feature> && gh pr create ...\n"
        )

    if not (RECEIPTS / f"{sha}.pr-shipper").exists():
        block(
            f"🚧 PR GATE — blocked. No fresh-eyes review on this commit ({sha[:8]}).\n\n"
            "Every PR gets a cold read by someone who did not build it. That is the whole point.\n\n"
            "NEXT STEP: dispatch the `pr-shipper` agent on this worktree. It reads the diff cold,\n"
            "runs gap-check, verifies the tests, reconciles against the plan's promises, writes the\n"
            "plain-English description, and opens the PR itself.\n\n"
            "Do NOT write the receipt by hand to get past this. That defeats the entire gate — and\n"
            "it is the exact shortcut this wall exists to prevent.\n"
        )

    # Sensitive diff? Then a security verdict is required too.
    # This ONE check fails CLOSED: `sh` returning None means the diff itself failed
    # (stale/missing origin/dev, timeout) — not that the diff is empty. Waiving the
    # security wall because git hiccuped is the worst possible default.
    files = sh(["git", "diff", "--name-only", "origin/dev...HEAD"], cwd=wd)
    if files is None:
        block(
            "🔒 SECURITY GATE — blocked. I couldn't read the diff against origin/dev, so I\n"
            "can't tell whether this change touches auth, permissions, or the schema.\n"
            "This gate fails closed on purpose.\n\n"
            f"NEXT STEP: git -C <worktree> fetch origin --prune   — then retry.\n"
        )
    hits = [
        f for f in files.splitlines()
        if SENSITIVE.search(f) or f.startswith(SENSITIVE_DIRS)
    ]
    if hits and not (RECEIPTS / f"{sha}.security").exists():
        listing = "\n".join(f"  · {f}" for f in hits[:10])
        more = f"\n  … and {len(hits) - 10} more" if len(hits) > 10 else ""
        block(
            f"🔒 SECURITY GATE — blocked. This change touches login, permissions, or the schema:\n\n"
            f"{listing}{more}\n\n"
            "In this system the danger is one restaurant seeing or changing another's data, so\n"
            "these changes get an independent verdict before they ship.\n\n"
            "NEXT STEP: dispatch the `security-auditor` agent. It returns BLOCK / FLAG / PASS.\n"
            "On PASS or FLAG it writes the receipt and this gate opens. On BLOCK it does not —\n"
            "which is correct, and means the hole must be fixed first.\n"
        )

    # Cleared to ship → the branch is now FROZEN (Wall 3). Done here, at the one point
    # every PR must pass through, precisely so that nobody has to remember to do it.
    branch = branch_of(wd)
    if branch:
        set_freeze(wd, branch, sha)


# ------------------------------------------------------ TRIPWIRE: the lane-diary gate
# Lane files are CURRENT STATE + links, not rolling journals (the board's own Rule 6).
# One lane file grew to 37KB (~9.4k tokens) and every session touching that lane paid
# to re-read months of closed history. Growing a lane file past the cap is blocked;
# shrinking (compacting) is always allowed — so an oversized lane gets compacted by
# its OWNING session the next time it writes, respecting lane ownership.
LANE_CAP = 10 * 1024


def lane_gate(tool, tool_input):
    if tool not in ("Edit", "Write"):
        return
    raw = tool_input.get("file_path") or ""
    if not re.search(r"/memory/lane-[^/]+\.md$", raw):
        return
    try:
        cur = Path(raw).stat().st_size
    except OSError:
        cur = 0
    if tool == "Write":
        new = len(tool_input.get("content", "") or "")
    else:
        new = cur - len(tool_input.get("old_string", "") or "") + len(
            tool_input.get("new_string", "") or ""
        )
    if new > LANE_CAP and new > cur:
        block(
            f"📔 LANE DIARY GATE — blocked. This write grows the lane file to ~{new // 1024}KB;"
            f" the cap is {LANE_CAP // 1024}KB.\n\n"
            "A lane file is CURRENT STATE + links (board Rule 6) — not a journal. Every\n"
            "session touching this lane re-reads the whole file; history belongs in its own\n"
            "project_*.md memory file, linked from the lane.\n\n"
            "NEXT STEP: move the closed chapters (old diagnoses, merge-night notes, batch\n"
            "evidence) into a project_<topic>_journal.md, keep current state + owed list +\n"
            "links here, then retry. Shrinking edits always pass.\n"
        )


# --------------------------------------------------- TRIPWIRE: the migration-name gate
# Migration filename discipline has burned deploys twice (2026-05-06 collision; the
# YYYYMMDD_HHMMSS truncation class): Supabase parses everything before the FIRST
# underscore as the version, so a 14-digit compact timestamp is mandatory and two
# files sharing a prefix collide on deploy. Prose rule → machine check.
def migration_check(path):
    s = str(path)
    if "supabase/migrations/" not in s or not s.endswith(".sql"):
        return
    name = path.name
    m = re.match(r"^(\d{14})_", name)
    if not m:
        block(
            f"🗓️ MIGRATION GATE — blocked. Bad migration filename:\n  {name}\n\n"
            "Migrations need a 14-digit compact timestamp prefix (NO underscore inside it):\n"
            "  $(date +%Y%m%d%H%M%S)_description.sql\n"
            "Supabase treats everything before the FIRST underscore as the version — a\n"
            "YYYYMMDD_HHMMSS name truncates to YYYYMMDD and collides with every other\n"
            "migration created that day.\n"
        )
    prefix = m.group(1)
    try:
        clash = [p.name for p in path.parent.glob(prefix + "_*") if p.name != name]
    except OSError:
        clash = []
    if clash:
        block(
            f"🗓️ MIGRATION GATE — blocked. Timestamp prefix {prefix} is already taken by:\n"
            + "\n".join(f"  · {c}" for c in clash)
            + "\n\nTwo migrations sharing a version prefix WILL break the deploy. Generate a\n"
            "fresh timestamp with `date +%Y%m%d%H%M%S` — never copy one from an existing file.\n"
        )


# --------------------------------------------------------- WALL 2: the worktree gate
def worktree_gate(tool, tool_input):
    if (HOME / ".claude" / ".allow-main-checkout").exists():
        return
    if tool not in ("Edit", "Write", "NotebookEdit"):
        return

    raw = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not raw:
        return
    try:
        path = Path(raw).resolve()
        rel = path.relative_to(REPO)
    except (ValueError, OSError):
        return  # outside this repo — not our business

    migration_check(path)  # applies everywhere in the repo, worktrees included

    # Cloud: each session has its own fresh clone, so the shared-checkout hazard this
    # wall guards against cannot happen. Migration discipline above still applies.
    if CLOUD:
        return

    if str(rel).startswith(".worktrees/"):
        return  # properly isolated — carry on
    if str(rel).startswith(MAIN_CHECKOUT_ALLOWED):
        return  # docs and config are fine to edit in place

    block(
        f"🚧 WORKTREE GATE — blocked. That's product code in the MAIN checkout:\n"
        f"  {rel}\n\n"
        "Several agents share this one folder. Editing code here silently contaminates or\n"
        "destroys whatever another session is holding — it has cost hours of git surgery before.\n\n"
        "NEXT STEP: work in your own isolated copy.\n"
        f"  git -C {REPO} fetch origin --prune\n"
        f"  git -C {REPO} worktree add .worktrees/<feature> -b feat/<project>-<topic> origin/dev\n"
        f"  cd {REPO}/.worktrees/<feature>\n\n"
        "…then make the same edit there. (Docs under docs/ are exempt and can be edited here.)\n"
    )


# The same wall, Bash edition: a shell mutates files and branch state just as
# destructively as the Edit tool, and it used to sail through unmatched. Both vectors
# below are from real incidents (2026-04-17 branch contamination; 2026-05-01 leftovers).
GIT_STATE = git_verb(r"checkout|switch|merge|rebase|stash\s+pop|reset")
WRITE_CMD = re.compile(r"\bsed\s+[^;|&]*-i|\bgit\s+apply\b")
# Lookbehind also excludes quote chars: HTML/JSX inside a heredoc (`lang="en">`)
# is not a shell redirect — that false positive fired for real on 2026-07-15.
REDIRECT = re.compile(r"(?<![<>&\w=\-'\"])\d?>{1,2}\s*([^\s;&|<>'\"\\]+)")
TEE = re.compile(r"\btee\s+(?:-\S+\s+)*([^\s;&|'\"]+)")


def _in_main_checkout(d):
    """Inside the shared main checkout (the repo, but not under .worktrees/)?"""
    try:
        rel = d.resolve().relative_to(REPO.resolve())
    except (ValueError, OSError, AttributeError):
        return False
    return not str(rel).startswith(".worktrees")


def _blocked_target(p):
    """A write target in the main checkout, outside the doc/config dirs?"""
    try:
        rel = p.resolve().relative_to(REPO.resolve())
    except (ValueError, OSError, AttributeError):
        return False
    s = str(rel)
    return not (s.startswith(".worktrees") or s.startswith(MAIN_CHECKOUT_ALLOWED))


def bash_worktree_gate(command, cwd):
    if (HOME / ".claude" / ".allow-main-checkout").exists():
        return
    # Cloud: one fresh clone per session, no shared checkout to protect. Skip entirely.
    if CLOUD:
        return

    # 1. Branch-state changes in the main checkout — checkout/switch/merge/rebase/
    #    reset/stash-pop. Parking the checkout back ON main/dev stays allowed (that is
    #    the repo-steward's legitimate job); switching to anything else is the exact
    #    contamination vector the worktree rule exists for.
    m = GIT_STATE.search(command)
    if m and not re.match(r"\s+(main|dev)\s*($|[;&|])", command[m.end():]):
        c = re.search(r"\bgit\b[^;|&]*?-C\s+([^\s;&|]+)", command[: m.end()])
        gwd = (
            Path(os.path.expanduser(c.group(1)))
            if c
            else effective_dir(command, cwd, before=m.start())
        )
        if _in_main_checkout(gwd):
            block(
                "🚧 WORKTREE GATE — blocked. That git command changes branch state in the\n"
                "shared MAIN checkout. Other sessions are working in this folder right now.\n\n"
                "Allowed here: parking back on main/dev (`git checkout dev`), fetch, log, status.\n"
                "Everything else happens in your own worktree:\n"
                f"  git -C {REPO} worktree add .worktrees/<feature> -b feat/<topic> origin/dev\n"
            )

    # 2. In-place file writes into the main checkout — sed -i, git apply, tee,
    #    shell redirects. Docs and agent config stay editable, same as the Edit tool.
    wd = effective_dir(command, cwd)
    targets = [t for t in REDIRECT.findall(command) if not t.startswith(("&", "/dev/"))]
    targets += TEE.findall(command)
    for t in targets:
        p = Path(os.path.expanduser(t))
        if not p.is_absolute():
            p = wd / t
        if _blocked_target(p):
            block(
                f"🚧 WORKTREE GATE — blocked. That command writes into the MAIN checkout:\n"
                f"  {t}\n\n"
                "Shell writes count the same as Edit-tool writes. Make the change in your own\n"
                "worktree (docs/ and .claude/ are exempt and fine to write here).\n"
            )
    if WRITE_CMD.search(command):
        abs_hits = [
            t
            for t in re.findall(re.escape(str(REPO)) + r"/[^\s;&|'\"]*", command)
            if _blocked_target(Path(t))
        ]
        if abs_hits or _in_main_checkout(wd):
            block(
                "🚧 WORKTREE GATE — blocked. sed -i / git apply mutates files in place, and\n"
                "this one points at the shared MAIN checkout. Run it inside your own worktree\n"
                "instead (docs/ and .claude/ are exempt).\n"
            )


# ------------------------------------------------------------ WALL 3: the freeze gate
def freeze_slug(branch):
    return branch.replace("/", "%")


def branch_of(wd):
    b = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=wd)
    return b if b and b != "HEAD" else None


def set_freeze(wd, branch, sha):
    """Called by Wall 1 the moment a PR is cleared to open. Nobody has to remember."""
    try:
        FREEZE.mkdir(parents=True, exist_ok=True)
        (FREEZE / freeze_slug(branch)).write_text(
            json.dumps({"branch": branch, "sha": sha, "frozen_at": int(time.time())})
        )
    except OSError:
        pass  # never block a legitimate PR because we couldn't write a marker


def freeze_gate(command, cwd):
    """A branch that has shipped its PR is CLOSED. New finding = new PR."""
    if (HOME / ".claude" / ".allow-frozen-branch").exists():
        return
    m = GIT_COMMIT_PUSH.search(command)
    if not m:
        return
    # The shipping command itself is exempt: `git push && gh pr create` is governed by
    # Wall 1, which writes the freeze marker BEFORE the command runs — without this
    # the marker blocks the very push that ships the PR (fired for real, PR #2571).
    if PR_CREATE.search(command):
        return

    wd = effective_dir(command, cwd, before=m.start())
    branch = branch_of(wd)
    if not branch:
        return
    marker = FREEZE / freeze_slug(branch)
    if not marker.exists():
        return  # not frozen — carry on

    # Markers expire after 14 days: a recycled topic name months later should not be
    # haunted by a long-merged PR's freeze.
    try:
        frozen_at = json.loads(marker.read_text()).get("frozen_at", 0)
        if frozen_at and (time.time() - float(frozen_at)) > 14 * 86400:
            marker.unlink()
            return
    except (OSError, ValueError, TypeError):
        pass

    # A merge in progress is exempt: resolving a conflict from dev is not new work,
    # and blocking it would leave the tree wedged mid-merge with no way out.
    git_dir = sh(["git", "rev-parse", "--absolute-git-dir"], cwd=wd)
    if git_dir and (Path(git_dir) / "MERGE_HEAD").exists():
        return

    # Docs-only commits are exempt: writing down what we found is never the problem.
    # What's STAGED is what ships — a stray unstaged code file must not block a
    # docs-only commit. Fall back to both lists only when nothing is staged (commit -a).
    staged = sh(["git", "diff", "--cached", "--name-only"], cwd=wd) or ""
    unstaged = sh(["git", "diff", "--name-only"], cwd=wd) or ""
    touched = [f for f in staged.splitlines() if f.strip()] or [
        f for f in unstaged.splitlines() if f.strip()
    ]
    if touched and all(f.startswith(("docs/", ".claude/")) for f in touched):
        return

    block(
        f"🧊 FREEZE GATE — blocked. Branch `{branch}` already shipped its PR. It is CLOSED.\n\n"
        "WHY: PR #2539 reached 100 commits and 22 security-audit rounds — not because the code\n"
        "was dangerous, but because the diff never stopped moving. Every fix folded into a\n"
        "shipped branch invalidated the last audit and bought another full round. That single\n"
        "habit is where ~34 of the 35 hours went.\n\n"
        "NEXT STEP — a new finding is a NEW PR:\n"
        f"  git -C {REPO} fetch origin --prune\n"
        f"  git -C {REPO} worktree add .worktrees/<new-topic> -b fix/<topic> origin/dev\n\n"
        "IF DIVYA EXPLICITLY SAID 'fold it in' — that is her override, and it is hers, not\n"
        "yours to assume:\n"
        "  touch ~/.claude/.allow-frozen-branch     (then TELL her you did, and remove it after)\n"
    )


# --------------------------------------------------------------- WALL 4: the box gate
def box_gate(tool, session_id=""):
    """No spending agents more than BOX_HOURS after Divya last spoke — IN THIS SESSION.

    The clock is reset ONLY by a UserPromptSubmit hook — i.e. only by HER typing. That is
    deliberate: a box I could reset myself is a box I would reset myself, at 4am, on
    commit 60. The only way past this wall is to actually stop and report to her.

    Per-session since 2026-07-15: on a multi-window day her typing anywhere used to
    reset EVERY window's box, so a runaway background lane was never actually boxed.
    Now each session is boxed by her last message in THAT session (falling back to the
    global stamp only for sessions with no per-session stamp yet).
    """
    if (HOME / ".claude" / ".allow-long-run").exists():
        return
    if tool not in SPENDING_TOOLS:
        return

    sid = re.sub(r"[^A-Za-z0-9_-]", "", str(session_id or ""))[:64]
    clock = CLOCK.parent / f".job-clock-{sid}" if sid else CLOCK
    if sid and not clock.exists():
        clock = CLOCK
    if not clock.exists():
        return  # no clock yet — first run of the session; don't block on our own gap

    try:
        last = float(json.loads(clock.read_text()).get("last_user_turn", 0))
    except (OSError, ValueError, AttributeError):
        return
    if not last:
        return

    elapsed = (time.time() - last) / 3600.0
    if elapsed <= BOX_HOURS:
        return

    block(
        f"⏱️  BOX GATE — blocked. {elapsed:.1f} hours since Divya last said anything, and you\n"
        f"are about to spend on another agent. The box is {BOX_HOURS:g} hours.\n\n"
        "WHY: the fleet debug ran ~35 hours unattended and consumed ~55% of a weekly budget.\n"
        "The org has quality gates but had no governor — agents never tire and never say\n"
        "'this has gone on too long.' This is the stop.\n\n"
        "NOTHING IS STRANDED: reading, editing, committing and pushing all still work. Only\n"
        "agent/workflow dispatch — the thing that actually costs money — is blocked.\n\n"
        "NEXT STEP: stop and report to her, in four lines:\n"
        "  · what is DIAGNOSED (cause proven, or still open?)\n"
        "  · what is FIXED and verified\n"
        "  · what is still OPEN — the list, not a promise to keep going\n"
        "  · what it has COST so far\n"
        "…then let her decide: extend, split, or park it.\n\n"
        "Her next message resets the clock. You cannot reset it yourself — that is the point.\n"
    )


def main():
    # On Divya's Mac the standalone ~/.claude/hooks/agent-guard.py already runs these
    # gates. This plugin copy stays silent locally so the two never double-fire; it
    # only takes over in the cloud sandbox, where that standalone copy does not exist.
    if not CLOUD:
        sys.exit(0)

    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # can't parse — never block on our own bug

    # Point the gates at whatever project this cloud session checked out.
    global REPO
    REPO = resolve_repo(payload.get("cwd"))

    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    cwd = payload.get("cwd")

    box_gate(tool, payload.get("session_id", ""))
    mcp_gate(tool, tool_input)
    lane_gate(tool, tool_input)

    if tool == "Bash":
        command = tool_input.get("command", "") or ""
        promote_gate(command, cwd)
        pr_gate(command, cwd)
        freeze_gate(command, cwd)
        bash_worktree_gate(command, cwd)
    else:
        worktree_gate(tool, tool_input)

    sys.exit(0)


if __name__ == "__main__":
    main()
