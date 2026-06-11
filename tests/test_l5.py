# ── Prospera SYSTEM HEADER (ADR-0032/SBOM) ──
# 性質:engineering ｜設計:Kevin 架構 ｜執行:AI 工具(claude.ai+Claude Code)
# 驗證:無機制驗證 ｜IP:創造性歸 Kevin(發明人), AI 為執行工具 (ADR-0032)
import pytest, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from monitoring_hook import trigger_monitoring, auto_remediate

def test_trigger():
    trigger_monitoring({'test': True})
    assert os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'execution_log.jsonl'))

def test_remediate():
    r = auto_remediate({'error': 'test'})
    assert r['status'] == 'ATTEMPTED'
