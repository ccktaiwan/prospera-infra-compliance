<!-- Prospera SYSTEM HEADER (ADR-0032/SBOM) | 性質:doc | 設計:Kevin 架構 | 執行:AI 工具(claude.ai+Claude Code) | 驗證:審計注入 | IP:創造性歸 Kevin(發明人) -->
# AGENTS.md — prospera-infra-compliance
# Version: 1.0 | 2026-04-30
# Governance Reference: prospera-constitution-governance v3.0
# Pipeline Reference: prospera-engine-workflow v1.0

## 1. REPO IDENTITY
Repo: ccktaiwan/prospera-infra-compliance
Layer: L3 — Compliance
Role: 合規中心

## 2. AGENT RULES

### PERMIT
- 讀取本 Repo 所有文件
- 執行 Decision Engine 四問法評估
- 生成稽核記錄（append-only）

### ESCALATE
- 修改核心定義 → J3
- 新增功能模組 → J2
- 外部整合 → J1

### BLOCK
- 繞過 Decision Engine 直接執行
- 不經稽核記錄的操作
- 自行合併 PR

## 3. Decision Engine
Q1 Should / Q2 Can / Q3 Fit / Q4 Profit
任一 BLOCK → 整體 BLOCK
任一 ESCALATE → 觸發對應 J點

## 4. J 點
J1 技術確認 / J2 品質審閱 / J3 架構決策

# Version: 1.0 | 2026-04-30
# 設計: 依 Kevin 架構 ｜執行: AI 工具(claude.ai+Claude Code) ｜驗證: 無機制驗證 ｜IP: 創造性歸 Kevin(發明人), AI 為執行工具 (ADR-0032)
## Living Organism Role
philosophy: PROSPERA_OS_PHILOSOPHY.md
organism_role: 皮膚屏障（外部掃描）
