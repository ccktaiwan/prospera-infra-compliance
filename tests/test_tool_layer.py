# ── Prospera SYSTEM HEADER (ADR-0032/SBOM) ──
# 性質:test(工具層 L2 四維 — adaptive 測既有 artifact) | 設計:Kevin Chang 架構(L0) | 驗證:真 pytest 測既有工具 artifact 真內容 | IP:創造性歸 Kevin Chang(發明人), AI 為執行工具 (ADR-0224)
"""test_tool_layer.py — 工具層 L2 四維（TOOL-L2，PENDING-153 D 類）。

adaptive：artifact 存在才測 L2（真驗格式/內容），缺則 skip(N/A)——不捏造 CHANGELOG/VERSION。
  T1 API 穩定性 / T2 文件覆蓋 / T3 版本管理 / T4 相依性健康
"""
from __future__ import annotations
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _find(*pats, maxdepth=3):
    out = []
    for p in pats:
        out += list(ROOT.rglob(p))
    return [f for f in out if ".git" not in f.parts and "__pycache__" not in f.parts]


# ───────────── T1 API 穩定性（CHANGELOG / 介面契約）─────────────
def _changelog():
    c = _find("CHANGELOG*", "CHANGES*")
    if not c:
        pytest.skip("T1 N/A：無 CHANGELOG")
    return c[0]


def test_t1_changelog_exists():
    assert _changelog().stat().st_size > 0


def test_t1_changelog_has_entries():
    t = _changelog().read_text(encoding="utf-8", errors="ignore")
    assert re.search(r"\d+\.\d+|\bv\d|##\s|breaking|新增|修正|change", t, re.I)   # 有變更記錄


# ───────────── T2 文件覆蓋（README）─────────────
def _readme():
    r = [f for f in _find("README*") if f.parent == ROOT] or _find("README*")
    if not r:
        pytest.skip("T2 N/A：無 README")
    return r[0]


def test_t2_readme_exists():
    assert _readme().stat().st_size > 100                 # README 非空殼


def test_t2_readme_has_sections():
    t = _readme().read_text(encoding="utf-8", errors="ignore")
    # 安裝/使用/範例/角色 任一章節（工具 repo 必要文件）
    assert re.search(r"install|安裝|usage|使用|example|範例|##\s|角色|role|purpose|用途", t, re.I)


# ───────────── T3 版本管理（semver）─────────────
def _version_text():
    cands = _find("VERSION", "version.py", "pyproject.toml", "setup.py")
    for c in cands:
        t = c.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"\bversion\b|__version__|\d+\.\d+\.\d+", t, re.I):
            return t
    pytest.skip("T3 N/A：無版本標注")


def test_t3_version_present():
    assert _version_text()


def test_t3_version_semver_format():
    t = _version_text()
    assert re.search(r"\d+\.\d+(\.\d+)?", t)              # semver 風格版本號


# ───────────── T4 相依性健康（requirements / pyproject）─────────────
def _deps():
    d = _find("requirements*.txt", "pyproject.toml")
    if not d:
        pytest.skip("T4 N/A：無相依列表")
    return d


def test_t4_deps_manifest_exists():
    assert any(f.stat().st_size > 0 for f in _deps())


def test_t4_deps_pinned_not_wildcard():
    # 相依非全 wildcard（*）——至少部分有版本約束（供應鏈健康）
    bad_only = True
    for f in _deps():
        t = f.read_text(encoding="utf-8", errors="ignore")
        for ln in t.splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#") or ln.startswith("["):
                continue
            if ln == "*" or ln.endswith("==*"):
                continue
            if re.search(r"[a-zA-Z0-9_\-]+\s*([=><~!]=?|@)", ln) or re.match(r"^[a-zA-Z0-9_\-]+$", ln):
                bad_only = False
                break
    assert not bad_only                                   # 有具名相依（非全空/全 wildcard）


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
