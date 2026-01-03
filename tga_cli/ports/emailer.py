# emailer.py  # interface for email sender

from __future__ import annotations
from pathlib import Path
from typing import Protocol


class EmailSender(Protocol):
    def send(self, attachment_paths: list[Path]) -> None: ...
