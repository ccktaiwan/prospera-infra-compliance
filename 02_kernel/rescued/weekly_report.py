"""
weekly_report.py  —  每週自動統計報告
每週一 09:00 執行，產生 reports/YYYY-WW.md，git commit 進 repo。

啟動：python weekly_report.py          (長駐模式，schedule 監聽)
手動：python weekly_report.py --now    (立即執行一次)
"""

import sys
import json
import logging
import datetime
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

try:
    import schedule
    import time
    _SCHEDULE = True
except ImportError:
    _SCHEDULE = False

from pipeline.audit import read_local_ledger
from pipeline.memory import get_stats

_MANIFEST = _HERE / "manifest.json"
_REPORTS  = _HERE / "reports"
_REPORTS.mkdir(exist_ok=True)
_REPO_ROOT = _HERE.parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [weekly-report] %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)
log = logging.getLogger("weekly-report")


# ── 資料收集 ──────────────────────────────────────────────────────────────────

def _load_manifest() -> list:
    if not _MANIFEST.exists():
        return []
    try:
        return json.loads(_MANIFEST.read_text(encoding="utf-8")).get("artifacts", [])
    except Exception:
        return []


def _this_week_range() -> tuple:
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return monday, sunday


def _week_label() -> str:
    today = datetime.date.today()
    return today.strftime("%Y-W%W")


def _count_bp_files() -> int:
    return len(list(_HERE.glob("best_practice_*.md")))


# ── 報告生成 ──────────────────────────────────────────────────────────────────

def generate_report() -> Path:
    artifacts = _load_manifest()
    ledger    = read_local_ledger()
    stats     = get_stats()

    monday, sunday = _this_week_range()
    week_label = _week_label()

    # 本週 artifacts
    week_artifacts = [
        a for a in artifacts
        if a.get("ingested_at", "")[:10] >= str(monday)
        and a.get("ingested_at", "")[:10] <= str(sunday)
    ]

    # 類型分佈
    type_count = Counter(a.get("type", "?") for a in artifacts)
    class_count = Counter(
        e.get("artifact_class", "other")
        for e in ledger
        if e.get("timestamp", "")[:10] >= str(monday)
    )

    # governance warning 統計
    warn_count = sum(
        1 for e in ledger
        if e.get("governance_status") == "warning"
        and e.get("timestamp", "")[:10] >= str(monday)
    )

    # 每週 artifact 趨勢（最近 4 週）
    weekly_counts = defaultdict(int)
    for a in artifacts:
        ts = a.get("ingested_at", "")
        if ts:
            try:
                d = datetime.date.fromisoformat(ts[:10])
                wk = d.strftime("%Y-W%W")
                weekly_counts[wk] += 1
            except Exception:
                pass

    recent_weeks = sorted(weekly_counts.keys())[-4:]

    # 報告內容
    lines = [
        f"# Artifact Registry 週報｜{week_label}",
        f"> 期間：{monday} ~ {sunday}",
        f"> 產生時間：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 本週摘要",
        "",
        f"| 指標 | 數值 |",
        f"|------|------|",
        f"| 本週新增 artifact | **{len(week_artifacts)}** |",
        f"| 總 artifact 數 | {stats.get('total', 0)} |",
        f"| Governance warnings | {warn_count} |",
        f"| Best-practice 文件 | {_count_bp_files()} |",
        "",
        "## 類型分佈（累計）",
        "",
    ]

    if type_count:
        lines += ["| 類型 | 數量 |", "|------|------|"]
        for t, n in type_count.most_common():
            lines.append(f"| {t} | {n} |")
    else:
        lines.append("_尚無資料_")

    lines += [
        "",
        "## 本週 Artifact 類別分佈",
        "",
    ]
    if class_count:
        lines += ["| 類別 | 數量 |", "|------|------|"]
        for c, n in class_count.most_common():
            lines.append(f"| {c} | {n} |")
    else:
        lines.append("_本週無 ingest 記錄_")

    lines += [
        "",
        "## 近 4 週趨勢",
        "",
        "| 週次 | 新增數 |",
        "|------|--------|",
    ]
    for wk in recent_weeks:
        lines.append(f"| {wk} | {weekly_counts[wk]} |")

    if week_artifacts:
        lines += [
            "",
            "## 本週新增清單",
            "",
            "| 標題 | 類型 | 時間 | Commit |",
            "|------|------|------|--------|",
        ]
        for a in week_artifacts[-20:]:  # 最多 20 筆
            ts = (a.get("ingested_at") or "")[:16].replace("T", " ")
            h  = (a.get("commit_hash") or "")[:7]
            lines.append(f"| {a.get('title','—')[:40]} | {a.get('type','?')} | {ts} | `{h}` |")

    lines += [
        "",
        "---",
        "",
        "_此報告由 artifact-registry/weekly_report.py 自動產生_",
    ]

    report_path = _REPORTS / f"{week_label}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    log.info(f"Report generated: {report_path}")
    return report_path


# ── Git commit ────────────────────────────────────────────────────────────────

def commit_report(report_path: Path):
    cwd = str(_REPO_ROOT)
    rel = report_path.relative_to(_REPO_ROOT)

    def run(cmd):
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

    run(["git", "add", str(rel)])
    r = run(["git", "commit", "-m", f"report: weekly {_week_label()}"])
    if r.returncode == 0:
        run(["git", "pull", "--rebase", "origin", "main"])
        run(["git", "push", "origin", "main"])
        log.info("Report committed and pushed")
    else:
        if "nothing to commit" not in r.stdout + r.stderr:
            log.warning(f"commit failed: {r.stderr}")


# ── 主排程 ────────────────────────────────────────────────────────────────────

def run_weekly():
    log.info("Running weekly report...")
    path = generate_report()
    commit_report(path)
    log.info(f"Done: {path.name}")


def main():
    force_now = "--now" in sys.argv

    if force_now:
        run_weekly()
        return

    if not _SCHEDULE:
        log.error("schedule package not installed. pip install schedule")
        sys.exit(1)

    log.info("Weekly report scheduler started. Runs every Monday at 09:00.")
    schedule.every().monday.at("09:00").do(run_weekly)

    # 進入等待循環
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
