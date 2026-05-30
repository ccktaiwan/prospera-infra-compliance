"""
pipeline/runner.py  —  共用 pipeline 執行核心
api_server.py 和 watch.py 都呼叫這裡，避免邏輯重複。
"""

import logging
import uuid
from pathlib import Path

from .ingest import ingest
from .commit import commit_and_push
from .audit  import log_artifact
from .memory import add_to_manifest, check_and_generate_best_practice

log = logging.getLogger("artifact-registry.runner")

_SUPPORTED = {".html", ".svg"}


def run(filepath: str, governance_fn=None) -> dict:
    """
    完整 pipeline：
      ingest → governance_check → manifest → git commit/push → audit → best-practice
    governance_fn(ingest_result) → governance_result dict（可選）
    """
    path = Path(filepath)
    if path.suffix.lower() not in _SUPPORTED:
        return {"ok": False, "reason": f"unsupported extension: {path.suffix}"}

    # 1. Ingest
    result = ingest(filepath)
    if not result["ok"]:
        log.error(f"[INGEST FAIL] {result.get('error')}")
        return result
    log.info(f"[INGEST] slug={result['slug']}  dest={result['dest']}")

    # 2. Governance check（可選，不 block）
    governance_result = {}
    if governance_fn:
        try:
            governance_result = governance_fn(result)
            if governance_result.get("warnings"):
                log.warning(f"[GOV] {governance_result['warnings']}")
        except Exception as e:
            log.warning(f"[GOV ERROR] {e}")

    # 3. Manifest（先用 pending，commit 後更新）
    manifest_entry = add_to_manifest(result, commit_hash="pending")
    artifact_id = manifest_entry.get("artifact_id", str(uuid.uuid4())[:8])

    # 4. Git commit + push
    commit_result = commit_and_push(result["slug"], result["type"], result["dest"])
    commit_hash = commit_result.get("commit_hash", "unknown")
    if commit_result["ok"]:
        log.info(f"[COMMIT] {commit_hash}")
        add_to_manifest(result, commit_hash)  # 補 real hash
    else:
        log.warning(f"[COMMIT WARN] {commit_result.get('error')}")

    # 5. Audit log
    audit_result = log_artifact(
        artifact_id=artifact_id,
        slug=result["slug"],
        commit_hash=commit_hash,
        artifact_type=result["type"],
        title=result["title"],
        description=result["description"],
    )
    log.info(f"[AUDIT] method={audit_result.get('method','?')}")

    # 6. Best-practice
    bp = check_and_generate_best_practice(result["type"])
    if bp.get("generated"):
        log.info(f"[BEST-PRACTICE] {bp['path']}")

    return {
        "ok":              True,
        "slug":            result["slug"],
        "type":            result["type"],
        "title":           result["title"],
        "dest":            result["dest"],
        "commit_hash":     commit_hash,
        "audit":           audit_result,
        "best_practice":   bp,
        "governance":      governance_result,
    }
