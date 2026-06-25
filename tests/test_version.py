# ── Prospera SYSTEM HEADER (ADR-0032/SBOM) ──
# 性質:test(工具層 T1/T3 — semver + CHANGELOG 真補驗證) | 設計:Kevin Chang 架構(L0) | 驗證:真 pytest | IP:創造性歸 Kevin Chang(發明人), AI 為執行工具 (ADR-0224)
"""test_version.py — 工具層 T3 版本管理 + T1 API 穩定（semver + CHANGELOG，PENDING-153 D 類真補）。"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


# ── T3 版本管理（semver）──
def test_version_file_exists():
    assert (ROOT / "VERSION").exists()


def test_version_is_semver():
    v = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert re.match(r"^\d+\.\d+\.\d+$", v), f"非 semver: {v}"   # X.Y.Z 語意版本


# ── T1 API 穩定性（CHANGELOG）──
def test_changelog_exists():
    assert (ROOT / "CHANGELOG.md").exists()


def test_changelog_has_unreleased_and_version():
    t = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "[Unreleased]" in t                                  # Keep a Changelog 標準
    assert re.search(r"\[\d+\.\d+\.\d+\]", t)                   # 有版本條目


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
