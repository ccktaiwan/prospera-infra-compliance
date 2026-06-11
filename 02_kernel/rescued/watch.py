# ── Prospera SYSTEM HEADER (ADR-0032/SBOM) ──
# 性質:engineering ｜設計:Kevin 架構 ｜執行:AI 工具(claude.ai+Claude Code)
# 驗證:無機制驗證 ｜IP:創造性歸 Kevin(發明人), AI 為執行工具 (ADR-0032)
"""
watch.py  —  Artifact Registry Watcher
監聽 inbox/ 資料夾，自動觸發完整 pipeline。

啟動：python watch.py
      make watch
"""

import sys
import time
import uuid
import logging
import os
from pathlib import Path

# 確保 pipeline 模組可被 import
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from pipeline.ingest import ingest
from pipeline.commit import commit_and_push
from pipeline.audit  import log_artifact
from pipeline.memory import add_to_manifest, check_and_generate_best_practice

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    _WATCHDOG = True
except ImportError:
    _WATCHDOG = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("artifact-registry")

_INBOX = _HERE / "inbox"
_INBOX.mkdir(exist_ok=True)
_SUPPORTED = {".html", ".svg"}


# ── Pipeline 觸發 ─────────────────────────────────────────────────────────────

def run_pipeline(filepath: str) -> dict:
    path = Path(filepath)
    if path.suffix.lower() not in _SUPPORTED:
        log.info(f"skip (unsupported): {path.name}")
        return {"ok": False, "reason": "unsupported extension"}

    log.info(f"[INGEST] {path.name}")

    # 1. Ingest：萃取 metadata，移動到 artifacts/
    result = ingest(filepath)
    if not result["ok"]:
        log.error(f"[INGEST FAIL] {result.get('error')}")
        return result
    log.info(f"  slug={result['slug']}  dest={result['dest']}")

    # 2. Manifest 更新（commit 前，產生 manifest.json）
    artifact_id = str(uuid.uuid4())[:8]
    manifest_entry = add_to_manifest(result, commit_hash="pending")
    artifact_id = manifest_entry["artifact_id"]

    # 3. Git commit + push
    log.info(f"[COMMIT] artifact: {result['slug']} [{result['type']}]")
    commit_result = commit_and_push(result["slug"], result["type"], result["dest"])
    commit_hash = commit_result.get("commit_hash", "unknown")

    # manifest 補上真實 commit hash
    manifest_entry["commit_hash"] = commit_hash
    add_to_manifest(result, commit_hash)   # 重新寫入（會去重）

    if not commit_result["ok"]:
        log.warning(f"[COMMIT WARN] {commit_result.get('error')}")
    else:
        log.info(f"  commit_hash={commit_hash}")

    # 4. Audit log
    log.info("[AUDIT] logging to ledger")
    audit_result = log_artifact(
        artifact_id=artifact_id,
        slug=result["slug"],
        commit_hash=commit_hash,
        artifact_type=result["type"],
        title=result["title"],
        description=result["description"],
    )
    log.info(f"  audit method={audit_result.get('method','?')}")

    # 5. Best-practice 檢查
    bp = check_and_generate_best_practice(result["type"])
    if bp.get("generated"):
        log.info(f"[BEST-PRACTICE] generated: {bp['path']}")

    log.info(f"[DONE] {result['slug']}")
    return {
        "ok":           True,
        "slug":         result["slug"],
        "type":         result["type"],
        "title":        result["title"],
        "dest":         result["dest"],
        "commit_hash":  commit_hash,
        "audit":        audit_result,
        "best_practice": bp,
    }


# ── Watchdog Handler ──────────────────────────────────────────────────────────

class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() in _SUPPORTED:
            time.sleep(0.5)   # 等待寫入完成
            run_pipeline(str(path))

    def on_moved(self, event):
        """支援把檔案拖入 inbox 的 move 事件"""
        if event.is_directory:
            return
        path = Path(event.dest_path)
        if path.suffix.lower() in _SUPPORTED and Path(event.dest_path).parent == _INBOX:
            time.sleep(0.5)
            run_pipeline(str(path))


# ── 啟動 ──────────────────────────────────────────────────────────────────────

def main():
    if not _WATCHDOG:
        log.error("watchdog 未安裝。請執行：pip install watchdog")
        sys.exit(1)

    log.info("=" * 50)
    log.info("Artifact Registry Watcher 啟動")
    log.info(f"監聽目錄：{_INBOX}")
    log.info(f"支援類型：{', '.join(_SUPPORTED)}")
    log.info("按 Ctrl+C 停止")
    log.info("=" * 50)

    observer = Observer()
    observer.schedule(InboxHandler(), str(_INBOX), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        log.info("Watcher 已停止")
    observer.join()


if __name__ == "__main__":
    main()
