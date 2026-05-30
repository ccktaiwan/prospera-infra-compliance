"""
api_server.py  —  Artifact Registry API Server
FastAPI, port 8765

POST /ingest          { html, title, description }
POST /ingest-url      { url }
GET  /status          → 最近 5 筆 artifact
GET  /health

啟動：python api_server.py
"""

import os
import sys
import json
import logging
import datetime
import re
from pathlib import Path
from typing import Optional

# ── path setup ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from pipeline.ingest import make_slug
from pipeline.runner import run as run_pipeline
from pipeline.memory import get_stats
from governance_check import check as governance_check

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

_INBOX   = _HERE / "inbox"
_INBOX.mkdir(exist_ok=True)
_MANIFEST = _HERE / "manifest.json"
_PID_FILE = _HERE / ".server.pid"

PORT = 8765

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("artifact-api")


# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Artifact Registry API",
    description="Receive artifacts from bookmarklet / browser extension",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # bookmarklet / extension 需要
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ── Models ────────────────────────────────────────────────────────────────────

class IngestPayload(BaseModel):
    html:        str
    title:       Optional[str] = ""
    description: Optional[str] = ""
    source_url:  Optional[str] = ""   # 來源頁面 URL（可選，用於記錄）


class IngestUrlPayload(BaseModel):
    url: str


# ── Helpers ───────────────────────────────────────────────────────────────────

def _write_inbox(content: str, title: str, ext: str = ".html") -> Path:
    """把內容寫到 inbox/，回傳路徑"""
    slug = make_slug(title or "untitled")
    filename = f"{slug}{ext}"
    path = _INBOX / filename
    # 避免覆蓋
    counter = 1
    while path.exists():
        path = _INBOX / f"{slug}_{counter}{ext}"
        counter += 1
    path.write_text(content, encoding="utf-8")
    return path


def _detect_ext(content: str) -> str:
    stripped = content.lstrip()
    if stripped.startswith("<svg") or stripped.startswith("<?xml"):
        return ".svg"
    return ".html"


def _inject_meta(html: str, title: str, description: str) -> str:
    """若 HTML 缺少 <title> 或 description，自動補入"""
    if title and "<title>" not in html.lower():
        html = html.replace("<head>", f"<head>\n<title>{title}</title>", 1)
        if "<title>" not in html.lower():
            html = f"<title>{title}</title>\n" + html
    if description and 'name="description"' not in html.lower():
        meta = f'<meta name="description" content="{description}">'
        html = html.replace("</head>", f"{meta}\n</head>", 1)
    return html


# ── Lifecycle ─────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    _PID_FILE.write_text(str(os.getpid()))
    log.info(f"Artifact Registry API server started (PID {os.getpid()})")
    log.info(f"  POST http://localhost:{PORT}/ingest")
    log.info(f"  POST http://localhost:{PORT}/ingest-url")
    log.info(f"  GET  http://localhost:{PORT}/status")


@app.on_event("shutdown")
async def shutdown():
    if _PID_FILE.exists():
        _PID_FILE.unlink()


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"ok": True, "port": PORT, "inbox": str(_INBOX)}


@app.get("/status")
def status():
    """回傳最近 5 筆 artifact + stats"""
    if not _MANIFEST.exists():
        return {"total": 0, "recent": [], "stats": {}}
    try:
        data = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    except Exception:
        return {"total": 0, "recent": [], "stats": {}}

    artifacts = data.get("artifacts", [])
    recent = artifacts[-5:][::-1]   # 最新 5 筆，倒序
    stats = get_stats()
    return {
        "total":  len(artifacts),
        "recent": [
            {
                "slug":          a.get("slug"),
                "title":         a.get("title"),
                "type":          a.get("type"),
                "ingested_at":   a.get("ingested_at"),
                "commit_hash":   a.get("commit_hash"),
            }
            for a in recent
        ],
        "stats": stats,
    }


@app.post("/ingest")
async def ingest(payload: IngestPayload):
    """
    接收 HTML/SVG 內容，寫入 inbox/，觸發完整 pipeline。
    """
    if not payload.html or len(payload.html.strip()) < 10:
        raise HTTPException(400, detail="html content too short or empty")

    title = (payload.title or "untitled").strip()[:120]
    ext   = _detect_ext(payload.html)

    # 補 metadata
    content = payload.html
    if ext == ".html":
        content = _inject_meta(content, title, payload.description or "")

    # 寫入 inbox
    inbox_path = _write_inbox(content, title, ext)
    log.info(f"[INGEST] received: {inbox_path.name}  source={payload.source_url or '—'}")

    # 執行 pipeline（含 governance check）
    result = run_pipeline(str(inbox_path), governance_fn=governance_check)

    if not result["ok"]:
        log.error(f"[PIPELINE FAIL] {result}")
        return JSONResponse(status_code=422, content={
            "ok": False,
            "error": result.get("error") or result.get("reason"),
        })

    gov = result.get("governance", {})
    log.info(f"[DONE] slug={result['slug']}  gov={gov.get('governance_status','?')}")

    return {
        "ok":               True,
        "slug":             result["slug"],
        "title":            result["title"],
        "type":             result["type"],
        "dest":             result["dest"],
        "commit_hash":      result["commit_hash"],
        "artifact_class":   gov.get("artifact_class", "other"),
        "governance_status": gov.get("governance_status", "ok"),
        "warnings":         gov.get("warnings", []),
    }


@app.post("/ingest-url")
async def ingest_url(payload: IngestUrlPayload):
    """
    Fetch URL 內容後走相同 pipeline。
    """
    try:
        import httpx
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(payload.url, headers={
                "User-Agent": "ArtifactRegistry/1.0 (local ingest)"
            })
            resp.raise_for_status()
            content = resp.text
    except Exception as e:
        raise HTTPException(400, detail=f"fetch failed: {e}")

    # 從 URL 萃取 title
    m = re.search(r"<title[^>]*>([^<]+)</title>", content, re.IGNORECASE)
    title = m.group(1).strip() if m else payload.url.split("/")[-1] or "untitled"

    return await ingest(IngestPayload(
        html=content,
        title=title,
        description="",
        source_url=payload.url,
    ))


# ── 啟動入口 ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",
        port=PORT,
        reload=False,
        log_level="info",
        app_dir=str(_HERE),
    )
