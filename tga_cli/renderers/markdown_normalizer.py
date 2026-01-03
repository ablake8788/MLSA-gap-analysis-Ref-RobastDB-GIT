# markdown_normalizer.py  # normalize_report_markdown

from __future__ import annotations

import re


class MarkdownNormalizer:
    def normalize(self, md: str) -> str:
        if not md:
            return md

        md = md.replace("\r\n", "\n").replace("\r", "\n")
        md = "\n".join(line.rstrip() for line in md.splitlines())
        md = re.sub(r"\n{3,}", "\n\n", md)

        # Remove horizontal rules
        md = re.sub(r"^\s*---\s*$", "", md, flags=re.MULTILINE)
        md = re.sub(r"\n{3,}", "\n\n", md)

        return md.strip() + "\n"
