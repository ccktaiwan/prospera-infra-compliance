# ============================================================
# AI HEADER
# SPEC_ID: PGC-L4-ENGINE-T15-v1.0
# MODULE: Title15_Audit_Pipeline
# LAYER: L4_ENGINE
# TYPE: Execution_Pipeline
# PURPOSE: Bridge canonical schema and kernel evaluation
# GOVERNANCE: CONTROLLED_EXECUTION
# VERSION: v1.0
# STATUS: ACTIVE
# ============================================================

import yaml
from 03_L3_KERNEL.evaluators.medical_evaluator import MedicalEvaluator

def run_audit(entity_application):
    """
    Execute audit process using canonical schema and kernel evaluator.
    """

    with open("02_REGISTRY/canonical/title_15_medical.yaml", "r") as f:
        schema = yaml.safe_load(f)

    kernel = MedicalEvaluator()

    results = []
    is_compliant = True

    for req in schema["requirements"]:

        success = kernel.evaluate(
            req["type"],
            entity_application.get(req["id"], {})
        )

        results.append({
            "requirement_id": req["id"],
            "passed": success,
            "severity": req["severity"]
        })

        if not success and req["severity"] == "BLOCKER":
            is_compliant = False

    return {
        "is_compliant": is_compliant,
        "details": results
    }
