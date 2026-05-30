"""
pipeline/audit.py  —  Audit Ledger
POST 到 http://localhost:9000/audit-ledger
fallback: 寫入本地 audit_local.jsonl
"""

import json
import datetime
from pathlib import Path

try:
    import requests as _requests
    _REQUESTS = True
except ImportError:
    _REQUESTS = False

_REGISTRY_ROOT  = Path(__file__).resolve().parents[1]
_LOCAL_LEDGER   = _REGISTRY_ROOT / "audit_local.jsonl"
_AUDIT_ENDPOINT = "http://localhost:9000/audit-ledger"
_TIMEOUT        = 3   # 秒，不阻塞主流程


def _write_local(entry: dict):
    with open(_LOCAL_LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def log_artifact(
    artifact_id: str,
    slug: str,
    commit_hash: str,
    artifact_type: str,
    title: str = "",
    description: str = "",
) -> dict:
    """
    向 audit-ledger 寫入一筆記錄。
    API 不通則 fallback 到 audit_local.jsonl。
    """
    entry = {
        "artifact_id":  artifact_id,
        "slug":         slug,
        "commit_hash":  commit_hash,
        "artifact_type": artifact_type,
        "title":        title,
        "description":  description,
        "timestamp":    datetime.datetime.now().isoformat(timespec="seconds"),
        "source":       "artifact-registry",
    }

    # 嘗試呼叫 API
    if _REQUESTS:
        try:
            resp = _requests.post(_AUDIT_ENDPOINT, json=entry, timeout=_TIMEOUT)
            if resp.status_code < 400:
                return {"ok": True, "method": "api", "status": resp.status_code}
        except Exception:
            pass   # fallback

    # Fallback：本地 JSONL
    try:
        _write_local(entry)
        return {"ok": True, "method": "local_fallback", "path": str(_LOCAL_LEDGER)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def read_local_ledger() -> list:
    if not _LOCAL_LEDGER.exists():
        return []
    entries = []
    with open(_LOCAL_LEDGER, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries
