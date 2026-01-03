# readers_image.py

from __future__ import annotations

import os
from pathlib import Path

import pytesseract
from PIL import Image

from tga_cli.config.ini_config import OcrSettings
from tga_cli.domain.errors import FatalError


class ImageReaderAdapter:
    def __init__(self, ocr: OcrSettings):
        if ocr.tesseract_path and os.path.exists(ocr.tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = ocr.tesseract_path

    def read(self, path: Path) -> str:
        try:
            return (pytesseract.image_to_string(Image.open(str(path))) or "").strip()
        except Exception as e:
            raise FatalError(f"Image OCR failed for file {path}. Error: {e}") from e
