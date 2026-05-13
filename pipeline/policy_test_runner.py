（一）governance/invocation/policy_test_runner.py
PASS = "PASS"
BLOCK = "BLOCK"
ESCALATE = "ESCALATE"

class PolicyDecision:
    def __init__(self, test_id, expected, actual, reason):
        self.test_id = test_id
        self.expected = expected
        self.actual = actual
        self.reason = reason

    def is_valid(self):
        return self.expected == self.actual


def evaluate_invocation(invocation):
    if invocation.get("actor") == "ai":
        return BLOCK, "AI actor is not permitted to invoke authority"

    if invocation.get("requires_human_authority") is True:
        return ESCALATE, "Human authority escalation required"

    if invocation.get("policy_violation") is True:
        return BLOCK, "Explicit policy violation detected"

    return PASS, "Invocation passes all governance checks"


def run_policy_tests(test_cases):
    results = []

    for case in test_cases:
        actual, reason = evaluate_invocation(case["input"])
        results.append(
            PolicyDecision(
                test_id=case["id"],
                expected=case["expected"],
                actual=actual,
                reason=reason
            )
        )

    return results
────────────────────────

（二）governance/ci/run_policy_tests.py
import sys
import json
from governance.invocation.policy_test_runner import run_policy_tests

POLICY_TESTS_PATH = "governance/invocation/policy_tests.json"

def main():
    with open(POLICY_TESTS_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    results = run_policy_tests(test_cases)
    failures = [r for r in results if not r.is_valid()]

    if failures:
        print("Policy Test Runner detected governance violations:")
        for f in failures:
            print(
                f"- Test {f.test_id}: expected {f.expected}, "
                f"got {f.actual} ({f.reason})"
            )
        sys.exit(1)

    print("All policy tests passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()

────────────────────────

（三）.github/workflows/policy_validation.yml
name: Prospera OS Policy Validation

on:
  pull_request:
    paths:
      - "governance/invocation/**"
      - "governance/ci/**"

jobs:
  policy-validation:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Run Policy Test Runner
        run: |
          python governance/ci/run_policy_tests.py


