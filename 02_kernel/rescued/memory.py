# ── Prospera SYSTEM HEADER (ADR-0032/SBOM) ──
# 性質:engineering ｜設計:Kevin 架構 ｜執行:AI 工具(claude.ai+Claude Code)
# 驗證:無機制驗證 ｜IP:創造性歸 Kevin(發明人), AI 為執行工具 (ADR-0032)
"""
pipeline/memory.py  —  Manifest & Best-Practice Generator
更新 manifest.json。累積 3 個同類型 artifact 時自動生成 best_practice_{type}.md
"""

import json
import datetime
from pathlib import Path
from collections import defaultdict

_REGISTRY_ROOT = Path(__file__).resolve().parents[1]
_MANIFEST      = _REGISTRY_ROOT / "manifest.json"
_BP_THRESHOLD  = 3   # 達到幾個同類型時生成 best practice


# ── manifest.json ─────────────────────────────────────────────────────────────

def _load_manifest() -> dict:
    if _MANIFEST.exists():
        try:
            return json.loads(_MANIFEST.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"version": "1.0", "updated_at": "", "artifacts": []}


def _save_manifest(data: dict):
    data["updated_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    _MANIFEST.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def add_to_manifest(ingest_result: dict, commit_hash: str) -> dict:
    """manifest.json に新エントリを追加し保存"""
    manifest = _load_manifest()

    entry = {
        "artifact_id":   f"{ingest_result['slug']}_{commit_hash[:7]}",
        "slug":          ingest_result["slug"],
        "title":         ingest_result["title"],
        "description":   ingest_result["description"],
        "type":          ingest_result["type"],
        "path":          ingest_result["dest"],
        "commit_hash":   commit_hash,
        "ingested_at":   ingest_result["timestamp"],
        "year":          ingest_result["year"],
        "month":         ingest_result["month"],
    }

    # 避免重複（同 slug）
    existing_slugs = {a["slug"] for a in manifest["artifacts"]}
    if entry["slug"] not in existing_slugs:
        manifest["artifacts"].append(entry)

    _save_manifest(manifest)
    return entry


# ── best_practice 生成 ────────────────────────────────────────────────────────

def _generate_best_practice(artifact_type: str, examples: list) -> str:
    lines = [
        f"# Best Practice: {artifact_type.upper()} Artifacts",
        f"> 自動生成 | 依據 {len(examples)} 個同類型 artifact 分析",
        f"> 更新時間：{datetime.datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## 已收錄的範例",
        "",
    ]
    for ex in examples:
        lines.append(f"- **{ex['title']}** (`{ex['slug']}`)")
        if ex.get("description"):
            lines.append(f"  {ex['description']}")
    lines += [
        "",
        "## 觀察到的模式",
        "",
        "| 維度 | 觀察 |",
        "|------|------|",
        f"| 類型 | {artifact_type} |",
        f"| 數量 | {len(examples)} 個 |",
        f"| 首次收錄 | {examples[0]['ingested_at'][:10] if examples else '—'} |",
        f"| 最新收錄 | {examples[-1]['ingested_at'][:10] if examples else '—'} |",
        "",
        "## 建議實踐",
        "",
        f"1. 每個 {artifact_type} artifact 應包含清晰的 `<title>` 標籤",
        "2. 使用 `<desc>` 或 `<meta name=description>` 描述用途",
        "3. 檔案命名採用 `YYYYMMDD_slug` 格式",
        "",
        "_此文件由 artifact-registry/pipeline/memory.py 自動生成_",
    ]
    return "\n".join(lines)


def check_and_generate_best_practice(artifact_type: str) -> dict:
    """同類型 artifact 達 threshold 時自動生成 best_practice_{type}.md"""
    manifest = _load_manifest()
    by_type = defaultdict(list)
    for a in manifest["artifacts"]:
        by_type[a["type"]].append(a)

    examples = by_type.get(artifact_type, [])
    if len(examples) < _BP_THRESHOLD:
        return {"generated": False, "count": len(examples), "threshold": _BP_THRESHOLD}

    bp_path = _REGISTRY_ROOT / f"best_practice_{artifact_type}.md"
    content = _generate_best_practice(artifact_type, examples)
    bp_path.write_text(content, encoding="utf-8")

    return {
        "generated": True,
        "path": str(bp_path),
        "artifact_count": len(examples),
    }


def get_stats() -> dict:
    manifest = _load_manifest()
    by_type = defaultdict(int)
    for a in manifest["artifacts"]:
        by_type[a["type"]] += 1
    return {
        "total": len(manifest["artifacts"]),
        "by_type": dict(by_type),
        "updated_at": manifest.get("updated_at", ""),
    }
