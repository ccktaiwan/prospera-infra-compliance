# CLAUDE.md — Prospera governance contract

**Authority**: ccktaiwan
**Schema**: prospera-os/DIRECTORY_SCHEMA.json
**Skills**: prospera-infra-ci/skills/SKILL-CORE.md
**Canonical source**: system_index.yaml v3.0

---

## EXECUTION MODEL

When working in any Prospera repo:
- NEVER produce manual scripts for the human to run
- ALWAYS use Claude Code to directly create files, run git, move directories
- If a task needs a decision → ask ccktaiwan ONE question, then execute
- The human judges. Claude Code executes.

---

## This repo

**Repo**: prospera-infra-compliance
**Status**: ACTIVE
**Tier**: L6 (Infra)
**Ring**: Ring 6 — Infrastructure

**Contract**:
- INPUT: Compliance check request + registry query
- OUTPUT: Compliance status + registry record

**Purpose**: Compliance product core, compliance_registry_core.py
