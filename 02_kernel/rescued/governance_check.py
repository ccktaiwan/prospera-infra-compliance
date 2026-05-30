"""
governance_check.py  —  Artifact Governance Checker
在 ingest 後執行，不 block，只標記 warning。
呼叫方式：result = check(ingest_result)
"""

import re
from pathlib import Path

_REGISTRY_ROOT = Path(__file__).resolve().parent

# ── 密鑰偵測 patterns ─────────────────────────────────────────────────────────
_SECRET_PATTERNS = [
    (re.compile(r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{20,}'), "api_key"),
    (re.compile(r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?[^\s"\']{8,}'),        "password"),
    (re.compile(r'(?i)bearer\s+[A-Za-z0-9_.~+/=-]{20,}'),                         "bearer_token"),
    (re.compile(r'AKIA[0-9A-Z]{16}'),                                              "aws_access_key"),
    (re.compile(r'(?i)(secret|private[_-]?key|token)\s*[:=]\s*["\']?[A-Za-z0-9_/+=\-]{20,}'),
                                                                                    "secret_token"),
    (re.compile(r'(?i)sk-[A-Za-z0-9]{32,}'),                                      "openai_key"),
    (re.compile(r'ghp_[A-Za-z0-9]{36}'),                                           "github_pat"),
]

# ── 類型分類 keywords ─────────────────────────────────────────────────────────
_TYPE_RULES = [
    ("dashboard",  re.compile(r'(?i)(dashboard|chart|graph|metric|kpi|gauge|統計|圖表|儀表)')),
    ("diagram",    re.compile(r'(?i)(diagram|flowchart|架構圖|流程圖|dataflow|<svg)')),
    ("form",       re.compile(r'(?i)(<form|<input|<select|<textarea|申請表|表單)')),
    ("report",     re.compile(r'(?i)(report|週報|月報|分析報告|summary)')),
    ("document",   re.compile(r'(?i)(document|specification|spec|規格|文件)')),
]


def _read_content(ingest_result: dict) -> str:
    dest = ingest_result.get("dest_abs") or (
        str(_REGISTRY_ROOT / ingest_result.get("dest", ""))
    )
    try:
        return Path(dest).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _check_metadata(content: str, ingest_result: dict) -> list:
    warnings = []
    title = ingest_result.get("title", "")
    if not title or title == "untitled":
        warnings.append("missing_title")
    desc = ingest_result.get("description", "")
    if not desc:
        if "<desc>" not in content and 'name="description"' not in content:
            warnings.append("missing_description")
    return warnings


def _check_secrets(content: str) -> list:
    found = []
    for pattern, label in _SECRET_PATTERNS:
        if pattern.search(content):
            found.append(label)
    return found


def _classify_type(content: str, ingest_result: dict) -> str:
    ext = ingest_result.get("type", "html")
    if ext == "svg":
        return "diagram"
    for type_label, pattern in _TYPE_RULES:
        if pattern.search(content):
            return type_label
    return "other"


def check(ingest_result: dict) -> dict:
    """
    ingest_result: pipeline.ingest.ingest() の戻り値
    Returns governance_result:
      {
        warnings: [],          # warning labels
        secret_hits: [],       # detected secret types
        artifact_class: str,   # dashboard/diagram/form/report/document/other
        governance_status: "ok" | "warning"
      }
    """
    content = _read_content(ingest_result)

    meta_warnings = _check_metadata(content, ingest_result)
    secret_hits   = _check_secrets(content)
    artifact_class = _classify_type(content, ingest_result)

    all_warnings = meta_warnings + [f"secret:{s}" for s in secret_hits]

    return {
        "warnings":         all_warnings,
        "secret_hits":      secret_hits,
        "artifact_class":   artifact_class,
        "governance_status": "warning" if all_warnings else "ok",
    }


# ── CLI smoke test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json

    fake = {
        "title": "",
        "description": "",
        "type": "html",
        "dest": "artifacts/test.html",
        "dest_abs": None,
    }
    # 建立假的 html 含密鑰
    tmp = _REGISTRY_ROOT / "artifacts" / "test.html"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(
        "<html><head></head><body>api_key='AKIAFAKEKEY1234567890' <form></form></body></html>",
        encoding="utf-8"
    )
    fake["dest_abs"] = str(tmp)

    result = check(fake)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    tmp.unlink()
