# ══════════════════════════════════════
# AI-GENERATED DOCUMENT
# ══════════════════════════════════════
# Generated:        2026-05-21T00:00:00Z
# Model:            claude-sonnet-4-6
# Phase:            Phase 5
# Layer:            L5
# Target Repo:      prospera-compliance-registry
# Governing Codex:  prospera-engineering-codex v1.0
# Human-Reviewed:   AI
# ══════════════════════════════════════
"""Compliance Registry Self-Monitor."""
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "02_kernel"))

MONITOR_LOG = Path(__file__).parent.parent / "reports" / "compliance_monitor.jsonl"


def run_monitor() -> dict:
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "component": "compliance-registry",
        "checks": {},
    }

    try:
        from compliance_registry_core import register_compliance, get_compliance_status
        register_compliance("health-check", "DNA-v1.0", "ok", {"monitor": "self-check"})
        entries = get_compliance_status()
        report["checks"]["registry"] = {
            "status": "ok",
            "total_entries": len(entries),
        }
    except Exception as ex:
        report["checks"]["registry"] = {"status": "fail", "error": str(ex)}

    all_ok = all(v.get("status") == "ok" for v in report["checks"].values())
    report["overall"] = "green" if all_ok else "yellow"

    MONITOR_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(MONITOR_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(report, ensure_ascii=False, default=str) + "\n")

    return report


if __name__ == "__main__":
    result = run_monitor()
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
