"""
pipeline/commit.py  —  Git Commit & Push
git add artifacts/ manifest.json → commit → push → return hash
"""

import subprocess
import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]   # prospera-global-inventory/


def _run(cmd: list, cwd: str) -> tuple:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def commit_and_push(slug: str, artifact_type: str, dest_rel: str) -> dict:
    """
    1. git add artifacts/ manifest.json audit_local.jsonl
    2. git commit -m "artifact: {slug} [{type}]"
    3. git pull --rebase（避免 push rejected）
    4. git push origin main
    Returns: { ok, commit_hash, error }
    """
    cwd = str(_REPO_ROOT)
    registry = str(_REPO_ROOT / "artifact-registry")

    # Stage artifacts + manifest + audit fallback
    add_targets = [
        os.path.join("artifact-registry", "artifacts"),
        os.path.join("artifact-registry", "manifest.json"),
        os.path.join("artifact-registry", "audit_local.jsonl"),
    ]
    rc, out, err = _run(["git", "add", "--"] + add_targets, cwd)
    if rc != 0:
        # 嘗試只 add 存在的檔案
        for t in add_targets:
            _run(["git", "add", t], cwd)

    # Commit
    msg = f"artifact: {slug} [{artifact_type}]"
    rc, out, err = _run(["git", "commit", "-m", msg], cwd)
    if rc != 0:
        if "nothing to commit" in out + err:
            return {"ok": True, "commit_hash": "no-change", "message": "nothing to commit"}
        return {"ok": False, "commit_hash": "", "error": f"commit failed: {err}"}

    # Parse commit hash
    commit_hash = ""
    for line in out.splitlines():
        if "main" in line or "master" in line:
            parts = line.split()
            for p in parts:
                if len(p) == 7 and p.isalnum():
                    commit_hash = p
                    break
    if not commit_hash:
        rc2, h, _ = _run(["git", "rev-parse", "--short", "HEAD"], cwd)
        commit_hash = h if rc2 == 0 else "unknown"

    # Pull --rebase then push
    _run(["git", "pull", "--rebase", "origin", "main"], cwd)
    rc, out, err = _run(["git", "push", "origin", "main"], cwd)
    if rc != 0:
        return {"ok": False, "commit_hash": commit_hash, "error": f"push failed: {err}"}

    return {"ok": True, "commit_hash": commit_hash, "pushed": True}
