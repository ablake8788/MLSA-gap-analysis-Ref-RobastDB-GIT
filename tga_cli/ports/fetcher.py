# fetcher.py                # interface for website fetch

from __future__ import annotations
from typing import Protocol


class WebsiteFetcher(Protocol):
    def fetch_text(self, url: str) -> str: ...
