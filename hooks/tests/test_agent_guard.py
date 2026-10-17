#!/usr/bin/env python3
"""Test rig for agent-guard.py.

Runs the hook as a subprocess, exactly as Claude Code does, with a crafted payload on
stdin. Each case gets a fresh temporary HOME (receipts, freeze markers and the job
clock live under it) and a fresh temporary git repository standing in for the project
(CLAUDE_PROJECT_DIR points at it, so the guard protects that repo). The expected verdict
is ALLOW (exit 0) or BLOCK (exit 2 with the gate's name on stderr).

Run from anywhere:  python3 hooks/tests/test_agent_guard.py
Exit status is the number of failing cases, so CI can use it directly.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

GUARD = Path(__file__).resolve().parents[1] / "agent-guard.py"


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def make_repo(tmp):
    """A project repo on branch feat/topic with origin/dev one commit behind."""
    repo = tmp / "project"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "dev")
    git(repo, "config", "user.email", "rig@example.com")
    git(repo, "config", "user.name", "rig")
    (repo / "README.md").write_text("project\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "init")
    git(repo, "remote", "add", "origin", "https://github.com/Owner/Repo")
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "update-ref", "refs/remotes/origin/dev", base)
    git(repo, "checkout", "-q", "-b", "feat/topic")
    (repo / "docs").mkdir()
    (repo / "docs" / "note.md").write_text("a note\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "docs: a note")
    return repo


def run_guard(payload, home, repo):
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["CLAUDE_PROJECT_DIR"] = str(repo)
    env.pop("CLAUDE_PLUGIN_ROOT", None)
    payload = dict(payload)
    payload.setdefault("cwd", str(repo))
    payload.setdefault("session_id", "rig")
    r = subprocess.run(
        [sys.executable, str(GUARD)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(repo),
        timeout=60,
    )
    return r.returncode, r.stderr


def bash(command):
    return {"tool_name": "Bash", "tool_input": {"command": command}}


def connector_pr(owner="Owner", repo="Repo", head="feat/topic"):
    return {
        "tool_name": "mcp__github__create_pull_request",
        "tool_input": {
            "owner": owner,
            "repo": repo,
            "head": head,
            "base": "dev",
            "title": "a title",
        },
    }


# ----------------------------------------------------------------- setup helpers
def with_shipper_receipt(home, repo):
    sha = git(repo, "rev-parse", "HEAD")
    d = home / ".claude" / "pr-receipts"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{sha}.pr-shipper").write_text("rig\n")


def with_freeze_marker(home, repo):
    d = home / ".claude" / "pr-freeze"
    d.mkdir(parents=True, exist_ok=True)
    (d / "feat%topic").write_text(
        json.dumps({"branch": "feat/topic", "sha": "x", "frozen_at": int(time.time())})
    )


def with_repo_freeze_off(home, repo):
    (repo / ".claude").mkdir(exist_ok=True)
    (repo / ".claude" / "no-branch-freeze").write_text("Wall 3 is OFF for this repository.\n")


def with_sensitive_commit(home, repo):
    (repo / "lib" / "auth").mkdir(parents=True)
    (repo / "lib" / "auth" / "session.ts").write_text("export const x = 1;\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "auth change")
    with_shipper_receipt(home, repo)


HEREDOC_TO_FILE = (
    "cat > docs/notes.md <<'EOF'\n"
    "Reminder: run gh pr create once the walk is done.\n"
    "EOF\n"
)
HEREDOC_TO_TEE = "tee docs/notes.md <<EOF\nlater: gh pr create\nEOF\n"
HEREDOC_TO_BASH = "bash <<'EOF'\ngh pr create --title t --body b\nEOF\n"
COMMIT_MESSAGE_HEREDOC = (
    "git commit -q --allow-empty -F - <<'MSG'\n"
    "Notes: the shipper runs gh pr create after review\n"
    "MSG\n"
)

CASES = [
    # name, payload, setup (or None), expected verdict, gate name expected on BLOCK
    ("CLI PR creation without a receipt is blocked",
     bash("gh pr create --title t --body b"), None, "BLOCK", "PR GATE"),
    ("CLI PR creation with a shipper receipt is allowed",
     bash("gh pr create --title t --body b"), with_shipper_receipt, "ALLOW", ""),
    ("the phrase inside a heredoc written to a file is not a PR",
     bash(HEREDOC_TO_FILE), None, "ALLOW", ""),
    ("the phrase inside a heredoc piped to tee is not a PR",
     bash(HEREDOC_TO_TEE), None, "ALLOW", ""),
    ("the phrase inside a heredoc fed to bash IS a PR and is blocked",
     bash(HEREDOC_TO_BASH), None, "BLOCK", "PR GATE"),
    ("the phrase inside a commit message heredoc is not a PR",
     bash(COMMIT_MESSAGE_HEREDOC), None, "ALLOW", ""),
    ("connector PR creation without a receipt is blocked",
     connector_pr(), None, "BLOCK", "PR GATE"),
    ("connector PR creation with a shipper receipt is allowed",
     connector_pr(), with_shipper_receipt, "ALLOW", ""),
    ("connector PR creation for another repository is not our business",
     connector_pr(owner="Someone", repo="Else"), None, "ALLOW", ""),
    ("connector PR creation on a sensitive diff needs a security receipt",
     connector_pr(), with_sensitive_commit, "BLOCK", "SECURITY GATE"),
    ("a push on a frozen branch is blocked",
     bash("git push origin feat/topic"), with_freeze_marker, "BLOCK", "FREEZE GATE"),
    ("a push on a frozen branch is allowed when the repo switched the wall off",
     bash("git push origin feat/topic"),
     lambda h, r: (with_freeze_marker(h, r), with_repo_freeze_off(h, r)), "ALLOW", ""),
    ("CLI PR creation on a sensitive diff needs a security receipt",
     bash("gh pr create --title t"), with_sensitive_commit, "BLOCK", "SECURITY GATE"),
]


def main():
    failures = 0
    for name, payload, setup, expected, gate in CASES:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            home = tmp / "home"
            home.mkdir()
            repo = make_repo(tmp)
            if setup:
                setup(home, repo)
            code, err = run_guard(payload, home, repo)
            verdict = "ALLOW" if code == 0 else "BLOCK"
            ok = verdict == expected and (verdict == "ALLOW" or gate in err)
            if not ok:
                failures += 1
            first = err.strip().splitlines()[0] if err.strip() else ""
            print(f"{'PASS' if ok else 'FAIL'}  {name}  ->  {verdict}  {first[:70]}")
    print(f"\n{len(CASES) - failures} of {len(CASES)} cases pass")
    return failures


if __name__ == "__main__":
    sys.exit(main())
