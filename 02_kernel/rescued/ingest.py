"""
pipeline/ingest.py  —  Artifact Ingest
讀取 HTML/SVG，萃取 metadata，移動到 artifacts/{year}/{month}/
"""

import os
import re
import shutil
import datetime
from pathlib import Path
from typing import Optional

try:
    from bs4 import BeautifulSoup
    _BS4 = True
except ImportError:
    _BS4 = False

_REGISTRY_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACTS_DIR = _REGISTRY_ROOT / "artifacts"


# ── metadata 萃取 ─────────────────────────────────────────────────────────────

def _extract_html_meta(content: str) -> dict:
    if _BS4:
        soup = BeautifulSoup(content, "html.parser")
        title = (soup.title.string.strip() if soup.title and soup.title.string else "")
        desc_tag = soup.find("meta", attrs={"name": "description"})
        desc = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else ""
        if not desc:
            h1 = soup.find("h1")
            desc = h1.get_text(strip=True) if h1 else ""
    else:
        m = re.search(r"<title[^>]*>([^<]+)</title>", content, re.IGNORECASE)
        title = m.group(1).strip() if m else ""
        m2 = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', content, re.IGNORECASE)
        desc = m2.group(1).strip() if m2 else ""
    return {"title": title or "untitled", "description": desc, "type": "html"}


def _extract_svg_meta(content: str) -> dict:
    if _BS4:
        soup = BeautifulSoup(content, "xml")
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""
        desc_tag = soup.find("desc")
        desc = desc_tag.get_text(strip=True) if desc_tag else ""
    else:
        m = re.search(r"<title[^>]*>([^<]+)</title>", content, re.IGNORECASE)
        title = m.group(1).strip() if m else ""
        m2 = re.search(r"<desc[^>]*>([^<]+)</desc>", content, re.IGNORECASE)
        desc = m2.group(1).strip() if m2 else ""
    return {"title": title or "untitled", "description": desc, "type": "svg"}


def extract_metadata(filepath: str) -> dict:
    path = Path(filepath)
    suffix = path.suffix.lower()
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"title": path.stem, "description": "", "type": suffix.lstrip("."), "error": str(e)}

    if suffix == ".html":
        return _extract_html_meta(content)
    elif suffix == ".svg":
        return _extract_svg_meta(content)
    else:
        return {"title": path.stem, "description": "", "type": suffix.lstrip(".")}


# ── slug 生成 ─────────────────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    text = re.sub(r"[^\w一-鿿\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text.strip())
    return text[:60].strip("-") or "untitled"


def make_slug(title: str, dt: Optional[datetime.datetime] = None) -> str:
    dt = dt or datetime.datetime.now()
    return f"{dt.strftime('%Y%m%d')}_{_slugify(title)}"


# ── 移動到 artifacts 目錄 ─────────────────────────────────────────────────────

def ingest(filepath: str) -> dict:
    """
    主入口：
    1. 萃取 metadata
    2. 生成 slug
    3. 移動到 artifacts/{year}/{month}/{slug}.{ext}
    返回 ingest_result dict
    """
    src = Path(filepath)
    if not src.exists():
        return {"ok": False, "error": f"File not found: {filepath}"}

    now = datetime.datetime.now()
    meta = extract_metadata(str(src))
    slug = make_slug(meta["title"], now)
    ext  = src.suffix.lower()

    dest_dir = _ARTIFACTS_DIR / str(now.year) / f"{now.month:02d}"
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest = dest_dir / f"{slug}{ext}"
    # 避免覆蓋：加後綴
    counter = 1
    while dest.exists():
        dest = dest_dir / f"{slug}_{counter}{ext}"
        counter += 1

    shutil.move(str(src), str(dest))

    return {
        "ok":          True,
        "slug":        slug,
        "type":        meta["type"],
        "title":       meta["title"],
        "description": meta["description"],
        "source":      src.name,
        "dest":        str(dest.relative_to(_REGISTRY_ROOT)),
        "dest_abs":    str(dest),
        "year":        now.year,
        "month":       now.month,
        "timestamp":   now.isoformat(timespec="seconds"),
    }
