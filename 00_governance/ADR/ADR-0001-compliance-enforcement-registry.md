<!-- Prospera SYSTEM HEADER (ADR-0032/SBOM) | 性質:architecture-decision | 設計:Kevin Chang 架構 | 執行:Claude Code | 驗證:git 實證(compliance_registry_core.py) | IP:創造性歸 Kevin Chang(發明人), AI 為執行工具 -->
# ADR-0001：合規執行基礎設施——compliance registry 為結構性 enforcement

- Status: Accepted ｜ Date: 2026-06-21 ｜ Ring: R6 Infra ｜ Type: A 服務型
- conception: Kevin Chang

## Context
合規（compliance）若靠各 repo 自律或事後稽核，會漏（codex_validation 原則：結構性 enforce 非 procedural）。本 repo（infra-compliance）負責**合規執行基礎設施**（compliance_registry_core.py + rescued/api_server/audit）。

## Decision
**合規以 registry 核心結構性 enforce**：①`compliance_registry_core.py` 為合規規則 registry（集中規則源）；②`rescued/audit.py` 提供稽核軌跡；③合規檢查結構性掛入流程（非事後抽查）。對齊 kernel codex_validation「結構性 enforce 而非 procedural」。

## Consequences
- 合規規則單一 registry；enforce 結構化可稽核。
- 誠實邊界：rescued/ 模組為從 archive 救援，需逐一驗 wiring；live enforce 待部署接線。

## Alternatives
- **各 repo 自律合規**：拒絕——漏檢、不一致。
- **僅事後稽核**：拒絕——違規已發生才發現（非結構性 enforce）。

## 真實性聲明
對應 infra-compliance 真實 code（compliance_registry_core/rescued/audit），非模板。
