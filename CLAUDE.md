# CLAUDE.md — Prospera governance contract

**Authority**: ccktaiwan
**Schema**: prospera-os/DIRECTORY_SCHEMA.json
**Skills**: prospera-ci-shared/skills/SKILL-CORE.md
**Canonical source**: system_index.yaml v3.0

---

## EXECUTION MODEL

When working in any Prospera repo:
- NEVER produce manual scripts for the human to run
- ALWAYS use Claude Code to directly create files, run git, move directories
- If a task needs a decision → ask ccktaiwan ONE question, then execute
- The human judges. Claude Code executes.

---

## Canonical root directories (13 total)

00_governance / 01_docs / 02_kernel / 03_engines / 04_workflows /
05_products / 06_memory / 07_data / 08_tools / 09_ip /
10_archive / 11_tests / 99_archive

FORBIDDEN root dirs (Pipeline Spec layer names are SUBDIR names only):
01_intent → 03_engines/intent_engine/
03_decomposition → 03_engines/decomposition/
04_execution → 04_workflows/execution/
05_validation → 08_tools/validation/
06_audit → 07_data/audit/
07_memory → 06_memory/
Any ALL_CAPS or PascalCase root dir → rename to lowercase

If a task needs a new root dir: STOP and report to ccktaiwan.

---

## This repo

**Repo**: prospera-compliance-registry
**Status**: UNKNOWN
**Tier**: UNKNOWN
