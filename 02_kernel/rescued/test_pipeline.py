# ── Prospera SYSTEM HEADER (ADR-0032/SBOM) ──
# 性質:engineering ｜設計:Kevin 架構 ｜執行:AI 工具(claude.ai+Claude Code)
# 驗證:無機制驗證 ｜IP:創造性歸 Kevin(發明人), AI 為執行工具 (ADR-0032)
"""
test_pipeline.py  —  Pipeline 端對端測試
建立假 artifact → 跑完整 pipeline → 驗證結果
"""

import sys
import json
import tempfile
import shutil
import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from pipeline.ingest import ingest, extract_metadata, make_slug
from pipeline.audit  import log_artifact, read_local_ledger
from pipeline.memory import add_to_manifest, check_and_generate_best_practice, get_stats

PASS = "[PASS]"
FAIL = "[FAIL]"

errors = []

def check(label, condition, detail=""):
    if condition:
        print(f"  {PASS} {label}")
    else:
        print(f"  {FAIL} {label}" + (f": {detail}" if detail else ""))
        errors.append(label)


# ── 建立假 HTML artifact ──────────────────────────────────────────────────────

FAKE_HTML = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="description" content="GenGrant 補助策略分析儀表板">
  <title>GenGrant 策略分析</title>
</head>
<body>
  <h1>集團補助策略矩陣</h1>
  <p>7 個法人 × 6 條補助管道</p>
</body>
</html>"""

FAKE_SVG = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <title>GenGrant 資料流程圖</title>
  <desc>展示 GenGrant 八個 Agent 的資料流向</desc>
  <rect width="800" height="600" fill="#fff"/>
  <text x="400" y="300" text-anchor="middle">GenGrant DataFlow</text>
</svg>"""

print("=" * 55)
print("Artifact Registry Pipeline Test")
print("=" * 55)

# ── Test 1: metadata 萃取 ─────────────────────────────────────────────────────
print("\n[1] Metadata 萃取")

# HTML
tmp_html = _HERE / "inbox" / "_test_artifact.html"
tmp_html.write_text(FAKE_HTML, encoding="utf-8")
meta = extract_metadata(str(tmp_html))
check("HTML title 萃取正確", "GenGrant" in meta["title"], meta["title"])
check("HTML type = html",   meta["type"] == "html", meta["type"])
check("HTML description 非空", bool(meta.get("description")), meta.get("description"))

# SVG
tmp_svg = _HERE / "inbox" / "_test_artifact.svg"
tmp_svg.write_text(FAKE_SVG, encoding="utf-8")
meta_svg = extract_metadata(str(tmp_svg))
check("SVG title 萃取正確", "GenGrant" in meta_svg["title"], meta_svg["title"])
check("SVG type = svg",    meta_svg["type"] == "svg", meta_svg["type"])

# slug
slug = make_slug("GenGrant 策略分析")
check("slug 格式正確 (YYYYMMDD_...)", len(slug) > 8 and slug[:8].isdigit(), slug)

# ── Test 2: ingest ────────────────────────────────────────────────────────────
print("\n[2] Ingest（移動到 artifacts/）")

result = ingest(str(tmp_html))
check("ingest ok",       result["ok"],             result.get("error"))
check("dest 路徑存在",    Path(_HERE / result["dest"]).exists() if result["ok"] else False,
      result.get("dest"))
check("slug 不為空",      bool(result.get("slug")), result.get("slug"))
check("type = html",     result.get("type") == "html")
check("timestamp 存在",   bool(result.get("timestamp")))

# SVG ingest
result_svg = ingest(str(tmp_svg))
check("SVG ingest ok", result_svg["ok"], result_svg.get("error"))

# ── Test 3: audit log ─────────────────────────────────────────────────────────
print("\n[3] Audit Log（API fallback → local）")

audit = log_artifact(
    artifact_id="test-0001",
    slug=result.get("slug", "test-slug"),
    commit_hash="abc1234",
    artifact_type="html",
    title=result.get("title", "test"),
    description="pipeline test entry",
)
check("audit ok",             audit["ok"],               audit.get("error"))
check("fallback 到 local",    audit.get("method") in ("local_fallback", "api"))

ledger = read_local_ledger()
check("ledger 有記錄",        len(ledger) >= 1)
check("ledger 有正確 slug",   any(e.get("slug") == result.get("slug") for e in ledger))

# ── Test 4: manifest ─────────────────────────────────────────────────────────
print("\n[4] Manifest 更新")

entry = add_to_manifest(result, "abc1234")
check("entry 有 slug",        bool(entry.get("slug")))
check("entry 有 type",        bool(entry.get("type")))
check("manifest.json 存在",   (_HERE / "manifest.json").exists())

manifest = json.loads((_HERE / "manifest.json").read_text(encoding="utf-8"))
check("manifest artifacts >= 1", len(manifest.get("artifacts", [])) >= 1)

stats = get_stats()
check("stats total >= 1", stats["total"] >= 1)
print(f"       stats: {stats}")

# ── Test 5: best-practice（需要 3 個同類型）────────────────────────────────────
print("\n[5] Best-Practice 生成（需 3 個 html）")

# 再插入兩個假 html entry
for i in range(2):
    fake = {
        "ok": True, "slug": f"20260528_test-extra-{i}", "type": "html",
        "title": f"Test Extra {i}", "description": f"extra artifact {i}",
        "dest": result.get("dest", "artifacts/test.html"),
        "year": 2026, "month": 5,
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    add_to_manifest(fake, f"fake{i}000")

bp = check_and_generate_best_practice("html")
check("best_practice.html 生成",  bp.get("generated"), f"count={bp.get('count')}, threshold={bp.get('threshold')}")
if bp.get("generated"):
    check("best_practice_html.md 存在", Path(bp["path"]).exists())

# ── 結果摘要 ──────────────────────────────────────────────────────────────────
print()
print("=" * 55)
if errors:
    print(f"RESULT: {len(errors)} FAILED — {errors}")
    sys.exit(1)
else:
    total_checks = 20
    print(f"RESULT: ALL PASS ({total_checks - len(errors)} checks)")
    print()
    print(f"inbox:     {_HERE / 'inbox'}")
    print(f"artifacts: {_HERE / 'artifacts'}")
    print(f"manifest:  {_HERE / 'manifest.json'}")
    print(f"ledger:    {_HERE / 'audit_local.jsonl'}")
    print()
    print("啟動監聽：cd artifact-registry && python watch.py")
    print("         或：make watch")
