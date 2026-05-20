# ══════════════════════════════════════
# AI-GENERATED DOCUMENT
# ══════════════════════════════════════
# Generated:        2026-05-20T00:00:00+08:00
# Model:            claude-sonnet-4-6
# Phase:            Phase 4 - Execution & Enforcement
# Layer:            L3 - Compliance
# Target Repo:      prospera-compliance-registry
# Governing Codex:  prospera-engineering-codex v1.0
# Human-Reviewed:   PENDING
# Review By:        PENDING
# Review Date:      PENDING
# ══════════════════════════════════════
# SPEC_ID: PGC-L4-ENGINE-T15-v1.0
# MODULE: Title15_Audit_Pipeline
# PURPOSE: Bridge canonical schema and kernel evaluation

import yaml
from pathlib import Path

from specs.medical_evaluator import MedicalEvaluator

_SCHEMA_PATH = Path(__file__).parent.parent / "specs" / "title_15_medical.yaml"


def run_audit(entity_application: dict) -> dict:
    """Execute audit process using canonical schema and kernel evaluator."""

    with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)

    kernel = MedicalEvaluator()
    results = []
    is_compliant = True

    for req in schema["requirements"]:
        success = kernel.evaluate(
            req["type"],
            entity_application.get(req["id"], {}),
        )
        results.append({
            "requirement_id": req["id"],
            "passed": success,
            "severity": req["severity"],
        })
        if not success and req["severity"] == "BLOCKER":
            is_compliant = False

    return {
        "is_compliant": is_compliant,
        "details": results,
    }
