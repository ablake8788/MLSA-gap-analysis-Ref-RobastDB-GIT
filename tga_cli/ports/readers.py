# readers.py  # interface for document reader
from __future__ import annotations
from pathlib import Path
from typing import Protocol


class DocumentReader(Protocol):
    def read(self, path: Path) -> str: ...
