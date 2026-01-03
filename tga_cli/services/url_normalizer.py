# services /
# __init__.py
# analysis_service.py  # main workflow orchestration
# baseline_policy.py  # baseline precedence rules (isolated)
# prompt_builder.py  # build_prompt only
# url_normalizer.py  # normalize_url + validate_http_url

from __future__ import annotations

import re
from urllib.parse import urlparse

from tga_cli.domain.errors import ValidationError


def normalize_url(url: str) -> str:
    s = (url or "").strip()
    if not s:
        return ""

    if re.match(r"^https?://", s, flags=re.IGNORECASE):
        return s

    parts = s.split("/", 1)
    host = parts[0].strip()
    rest = ("/" + parts[1]) if len(parts) > 1 else ""

    if "." not in host and host.lower() not in {"localhost"}:
        host = host + ".com"

    return "https://" + host + rest


def validate_http_url(url: str, label: str) -> str:
    u = normalize_url(url)
    if not u:
        raise ValidationError(f"{label} URL is blank.")

    parsed = urlparse(u)
    if parsed.scheme not in ("http", "https"):
        raise ValidationError(f"{label} URL must be http/https: '{u}'")
    if not parsed.netloc:
        raise ValidationError(f"{label} URL is invalid (missing host): '{u}'")

    host = parsed.netloc.split("@")[-1].split(":")[0].strip().lower()
    if host != "localhost" and "." not in host:
        raise ValidationError(f"{label} URL host looks invalid: '{host}' (did you mean '{host}.com'?)")

    return u
