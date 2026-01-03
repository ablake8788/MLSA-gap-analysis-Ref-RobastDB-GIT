# fetch_requests.py         # requests + BS4 (+ readability) adapter

from __future__ import annotations

import re
import logging
import requests
from bs4 import BeautifulSoup

from tga_cli.domain.errors import FatalError
from tga_cli.services.url_normalizer import validate_http_url

logger = logging.getLogger("tga_cli")

try:
    from readability import Document as ReadabilityDocument
except Exception:
    ReadabilityDocument = None


class RequestsFetcher:
    def __init__(self, *, timeout_seconds: int = 25):
        self._timeout = timeout_seconds

    def fetch_text(self, url: str) -> str:
        url = validate_http_url(url, "Website")
        headers = {"User-Agent": "Mozilla/5.0 (TitaniumTGA/1.0)"}

        try:
            r = requests.get(url, headers=headers, timeout=self._timeout)
            r.raise_for_status()
        except requests.exceptions.Timeout:
            raise FatalError(f"Timed out fetching URL: {url}")
        except requests.exceptions.HTTPError as e:
            status = getattr(e.response, "status_code", "unknown")
            raise FatalError(f"HTTP error fetching URL ({status}): {url}")
        except requests.exceptions.RequestException as e:
            raise FatalError(f"Network error fetching URL: {url} ({e})")

        html = r.text

        if ReadabilityDocument:
            try:
                doc = ReadabilityDocument(html)
                summary_html = doc.summary(html_partial=True)
                title = doc.short_title()
                soup = BeautifulSoup(summary_html, "lxml")
                text = soup.get_text("\n", strip=True)
                return f"Title: {title}\nURL: {url}\n\n{text}".strip()
            except Exception:
                pass

        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()
        text = soup.get_text("\n", strip=True)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return f"URL: {url}\n\n{text}".strip()
