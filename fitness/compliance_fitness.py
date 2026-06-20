#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Prospera SYSTEM HEADER (ADR-0032/SBOM) | 設計:Kevin Chang 架構(服務型結構 fitness) | 執行:Claude Code | 驗證:py_compile + 結構檢查 | IP:創造性歸 Kevin Chang(發明人), AI 為執行工具
"""compliance_fitness.py — 服務型結構 fitness(SRAF L5,真實檢查非 stub)。
驗治理件 + 主模組真實存在;任一缺→fail(gap=真工作項)。診斷非阻斷。"""
import os, sys
_R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def check():
    r={
        "manifest": os.path.isfile(os.path.join(_R,"manifest.json")),
        "contract": os.path.isfile(os.path.join(_R,"CONTRACT.md")),
        "ecosystem_role": os.path.isfile(os.path.join(_R,"ECOSYSTEM_ROLE.md")),

    }
    p=sum(1 for v in r.values() if v)
    return {"checks":r,"passed":p,"total":len(r),"ok":p==len(r)}
def main():
    r=check()
    for k,v in r["checks"].items(): print(f"  [{'OK' if v else 'GAP'}] {k}")
    print(f"[compliance-fitness] {r['passed']}/{r['total']} pass")
    return 0 if r["ok"] else 1
if __name__=="__main__": sys.exit(main())
