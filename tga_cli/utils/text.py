from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urlparse


def truncate(text: str, max_chars: int) -> str:
    text = text or ""
    return text if len(text) <= max_chars else text[: max_chars - 200] + "\n\n[TRUNCATED]\n"


def safe_slug(text: str, max_len: int = 60) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"^https?://", "", text)
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:max_len] if text else "unknown"


def competitor_slug_from_url(url: str) -> str:
    try:
        host = urlparse(url).netloc or urlparse("https://" + url).netloc
    except Exception:
        host = url
    host = host.lower()
    host = re.sub(r"^www\.", "", host)
    return safe_slug(host)


def build_report_base_name(competitor_url: str) -> str:
    comp = competitor_slug_from_url(competitor_url)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"comparison_report_{comp}_{stamp}"
