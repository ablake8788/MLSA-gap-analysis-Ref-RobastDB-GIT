# readers_pdf.py            # pypdf + pdf2image + tesseract adapter

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pytesseract
from pypdf import PdfReader

from tga_cli.config.ini_config import OcrSettings
from tga_cli.domain.errors import FatalError


class PdfReaderAdapter:
    def __init__(self, ocr: OcrSettings):
        self._ocr = ocr
        if ocr.tesseract_path and os.path.exists(ocr.tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = ocr.tesseract_path

    def read(self, path: Path) -> str:
        txt = self._read_pdf_text(path)
        if txt.strip():
            return txt
        return self._read_pdf_ocr(path)

    def _read_pdf_text(self, path: Path) -> str:
        reader = PdfReader(str(path))
        out: list[str] = []
        for i, page in enumerate(reader.pages):
            t = page.extract_text() or ""
            if t.strip():
                out.append(f"\n Page {i + 1} \n{t}")
        return "\n".join(out).strip()

    def _read_pdf_ocr(self, path: Path) -> str:
        try:
            from pdf2image import convert_from_path
        except Exception:
            raise FatalError("pdf2image is not installed; install it to enable OCR fallback for scanned PDFs.")

        try:
            pages = convert_from_path(str(path), dpi=self._ocr.pdf_dpi)
        except Exception as e:
            raise FatalError(
                "Failed to convert PDF pages for OCR (often Poppler missing).\n"
                f"File: {path}\nError: {e}"
            )

        out: list[str] = []
        for i, page_img in enumerate(pages, start=1):
            try:
                page_text = pytesseract.image_to_string(page_img)
            except Exception as e:
                raise FatalError(f"OCR failed on page {i}. Error: {e}")
            out.append(f"\n Page {i} OCR Text \n{(page_text or '').strip()}")
        return "\n".join(out).strip()
