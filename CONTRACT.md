<!-- Prospera SYSTEM HEADER (ADR-0032/SBOM) | 性質:idea | 設計:Kevin 架構 | 執行:AI 工具(claude.ai+Claude Code) | 驗證:無機制驗證 | IP:創造性歸 Kevin(發明人), AI 為執行工具 -->
# CONTRACT｜prospera-infra-compliance
Ring: R6 Infrastructure
Version: v1.0
Date: 2026-05-31

## 定位
合規基礎設施。自動化合規掃描和報告。

## Input
| 欄位 | 型別 | 必填 | 說明 |
|------|------|------|------|
| scan_target | string | ✅ | 目標 repo 或路徑 |

## Output
| 欄位 | 型別 | 說明 |
|------|------|------|
| compliance_report | object | 合規掃描報告 |
| violations | array | 違規項目 |

## Boundary
- 只讀，不修改任何 repo
- 掃描結果寫入 prospera-standard-audit

## Governing Spec
Spec: prospera-standard-compliance
Reference Type: semantic
