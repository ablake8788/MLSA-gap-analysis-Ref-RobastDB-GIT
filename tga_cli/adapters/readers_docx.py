# readers_docx.py

from __future__ import annotations

from pathlib import Path
from docx import Document as DocRead


class DocxReaderAdapter:
    def read(self, path: Path) -> str:
        d = DocRead(str(path))
        return "\n".join(p.text for p in d.paragraphs if p.text.strip()).strip()
