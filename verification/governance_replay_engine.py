（一）governance/verification/replay_scenarios_v1.0.yaml
meta:
  name: Prospera OS Governance Replay Scenarios
  version: v1.0
  scope: stage_3_to_stage_5
  purpose: verification_and_audit

scenarios:

  - scenario_id: REPLAY_001
    description: Valid human-authorized invocation
    invocation:
      actor: human
      requires_human_authority: false
      policy_violation: false
    execution:
      worker_profile:
        id: worker_001
        role: engineering_worker
        allowed_scopes: [analysis]
      context:
        scope: analysis
    generation:
      content:
        format: codex_spec
        style: formal
    expected_outcome: PASS

  - scenario_id: REPLAY_002
    description: AI attempts authority invocation
    invocation:
      actor: ai
      requires_human_authority: false
      policy_violation: false
    expected_outcome: BLOCK

  - scenario_id: REPLAY_003
    description: Invocation requiring human escalation
    invocation:
      actor: human
      requires_human_authority: true
      policy_violation: false
    expected_outcome: ESCALATE

────────────────────────

（二）governance/verification/governance_replay_engine.py
from governance.invocation.policy_test_runner import evaluate_invocation
from sdk.enforcement.execution_adapter import ExecutionAdapter
from sdk.enforcement.generation_adapter import GenerationAdapter

def run_replay_scenario(scenario):
    outcome, reason = evaluate_invocation(scenario["invocation"])

    if outcome != scenario["expected_outcome"]:
        return False, f"Invocation mismatch: {reason}"

    if outcome != "PASS":
        return True, f"Replay ended at {outcome}"

    execution = scenario["execution"]
    adapter = ExecutionAdapter(execution["worker_profile"])
    adapter.bind_execution(execution["context"])

    generation = scenario["generation"]
    generator = GenerationAdapter({"required_format": "codex_spec"})
    generator.render(generation["content"])

    return True, "Replay PASS through Stage 3–5"

（三）governance/ci/run_governance_replay.py
import sys
import yaml
from governance.verification.governance_replay_engine import run_replay_scenario

SCENARIOS_PATH = "governance/verification/replay_scenarios_v1.0.yaml"

def main():
    with open(SCENARIOS_PATH, "r", encoding="utf-8") as f:
        scenarios = yaml.safe_load(f)["scenarios"]

    failures = []

    for s in scenarios:
        success, message = run_replay_scenario(s)
        if not success:
            failures.append((s["scenario_id"], message))

    if failures:
        print("Governance replay failed:")
        for fid, msg in failures:
            print(f"- {fid}: {msg}")
        sys.exit(1)

    print("All governance replay scenarios passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
────────────────────────

（四）.github/workflows/governance_replay.yml
name: Prospera OS Governance Replay Verification

on:
  pull_request:
  workflow_dispatch:

jobs:
  governance-replay:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install pyyaml

      - name: Run Governance Replay
        run: |
          python governance/ci/run_governance_replay.py
