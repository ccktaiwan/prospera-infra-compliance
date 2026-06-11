# ── Prospera SYSTEM HEADER (ADR-0032/SBOM) ──
# 性質:engineering ｜設計:Kevin 架構 ｜執行:AI 工具(claude.ai+Claude Code)
# 驗證:無機制驗證 ｜IP:創造性歸 Kevin(發明人), AI 為執行工具 (ADR-0032)
from pathlib import Path
REPO_ROOT = Path(__file__).parent.parent

def test_contract_exists():
    assert (REPO_ROOT / "CONTRACT.md").exists(), "CONTRACT.md missing"

def test_agents_exists():
    assert (REPO_ROOT / "AGENTS.md").exists(), "AGENTS.md missing"

def test_maturity_declaration_exists():
    assert (REPO_ROOT / "REPOSITORY_MATURITY_DECLARATION.md").exists()

def test_gitignore_has_pycache():
    gi = (REPO_ROOT / ".gitignore").read_text(errors="ignore") if (REPO_ROOT / ".gitignore").exists() else ""
    assert "__pycache__" in gi, ".gitignore missing __pycache__"
