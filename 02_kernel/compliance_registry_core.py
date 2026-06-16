# Prospera SYSTEM HEADER (ADR-0032/SBOM) | 性質:engineering | 設計:Kevin 架構 | 執行:AI 工具(claude.ai+Claude Code) | 驗證:審計注入 | IP:創造性歸 Kevin(發明人)
# AI-GENERATED | Model: claude-sonnet-4-6 | Phase: 5 | IP: 創造性歸 Kevin(發明人), AI 為執行工具 (ADR-0032)
"""Compliance Registry Core — register and query repo compliance status."""
import json
from datetime import datetime, timezone
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent / "07_data"
_REGISTRY_PATH = _DATA_DIR / "compliance_registry.jsonl"


def register_compliance(repo: str, framework: str, status: str, evidence: dict = None) -> dict:
    entry = {
        "repo": repo, "framework": framework, "status": status,
        "evidence": evidence or {},
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_REGISTRY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def get_compliance_status(repo: str = None) -> list:
    if not _REGISTRY_PATH.exists():
        return []
    entries = []
    with open(_REGISTRY_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line.strip())
                if repo is None or e.get("repo") == repo:
                    entries.append(e)
            except Exception:
                continue
    return entries


if __name__ == "__main__":
    register_compliance("prospera-os", "DNA-v1.0", "compliant", {"level": 5})
    register_compliance("prospera-exam-platform", "DNA-v1.0", "compliant", {"level": 5})
    status = get_compliance_status()
    print(f"Registry entries: {len(status)}")
    for s in status:
        print(f"  {s['repo']}: {s['status']}")
