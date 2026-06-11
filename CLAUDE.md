<!-- Prospera SYSTEM HEADER (ADR-0032/SBOM) | 性質:doc | 設計:Kevin 架構 | 執行:AI 工具(claude.ai+Claude Code) | 驗證:無機制驗證 | IP:創造性歸 Kevin(發明人), AI 為執行工具 -->
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
- If a task needs a decision -- ask ccktaiwan ONE question, then execute
- The human judges. Claude Code executes.

---

## This repo

**Ring**:    Ring 6
**Tier**:    L6 — Infrastructure
**Input**:   Compliance events
**Output**:  Compliance report → dashboard
**Owner**:   compliance pipeline
