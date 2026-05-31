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
