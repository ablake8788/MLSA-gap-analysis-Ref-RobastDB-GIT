# app_factory.py
####
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from tga_cli.services.processor_router import ProcessorRouter

from tga_cli.config.ini_config import IniConfig, INI_DEFAULT_NAME
from tga_cli.logging.setup import setup_logging

from tga_cli.adapters.fetch_requests import RequestsFetcher
from tga_cli.adapters.llm_openai import OpenAILlmClient
from tga_cli.adapters.email_smtp import SmtpEmailSender
from tga_cli.adapters.readers_pdf import PdfReaderAdapter
from tga_cli.adapters.readers_docx import DocxReaderAdapter
from tga_cli.adapters.readers_image import ImageReaderAdapter
from tga_cli.adapters.sqlserver_presets import SqlServerPresetRepository

from tga_cli.renderers.markdown_normalizer import MarkdownNormalizer
from tga_cli.renderers.html_renderer import HtmlRenderer
from tga_cli.renderers.docx_renderer import DocxRenderer
from tga_cli.renderers.pptx_renderer import PptxRenderer
from tga_cli.repositories.report_repository import ReportRepository
from tga_cli.services.analysis_service import AnalysisService
def _resolve_ini_path(ini_path: Optional[str]) -> Path:
    """
    Resolve ini path in a way that works both for normal Python and PyInstaller.
    Priority:
      1) explicit ini_path argument (if provided)
      2) APP_INI env var (if set)
      3) default next to exe (PyInstaller) or project default (dev)
    """
    env_ini = (os.getenv("APP_INI") or "").strip()
    raw = (ini_path or "").strip() or env_ini

    if raw:
        p = Path(raw)
        if not p.is_absolute():
            base = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path.cwd()
            p = base / p
        return p.resolve(strict=False)

    if getattr(sys, "frozen", False):
        return (Path(sys.executable).resolve().parent / INI_DEFAULT_NAME).resolve(strict=False)

    return (Path(__file__).resolve().parents[2] / INI_DEFAULT_NAME).resolve(strict=False)


def _build_settings(cfg: IniConfig):
    """
    Convert IniConfig -> AppSettings.

    In your codebase, IniConfig already defines:
        def load_settings(self) -> AppSettings
    so the correct implementation is simply calling it.
    """
    return cfg.load_settings()


def create_app(ini_path: str = "TIS_GapAnalysis_Ref_RobastDB.ini") -> Dict[str, Any]:
    """
    Composition root for CLI + Flask.
    Returns wired AnalysisService plus preset_repo.
    """
    log = logging.getLogger("tga_cli")

    resolved_ini = _resolve_ini_path(ini_path)
    log.info("create_app: resolved ini=%s", resolved_ini)

    # Create IniConfig from the resolved path.
    # If IniConfig has from_path() use it; otherwise force APP_INI and use from_env_or_default().
    if hasattr(IniConfig, "from_path"):
        cfg = IniConfig.from_path(str(resolved_ini))
    else:
        os.environ["APP_INI"] = str(resolved_ini)
        cfg = IniConfig.from_env_or_default()

    settings = _build_settings(cfg)

    setup_logging(settings.logging.level)
    log.info("create_app: logging=%s", settings.logging.level)

    # ---- Infrastructure adapters ----
    llm = OpenAILlmClient(api_key=settings.openai.api_key, model=settings.openai.model)
    fetcher = RequestsFetcher(timeout_seconds=settings.http.timeout_seconds)

    emailer = None
    if settings.email.enabled:
        emailer = SmtpEmailSender(settings.email)

    readers = {
        ".pdf": PdfReaderAdapter(settings.ocr),
        ".docx": DocxReaderAdapter(),
        ".jpg": ImageReaderAdapter(settings.ocr),
        ".jpeg": ImageReaderAdapter(settings.ocr),
        ".png": ImageReaderAdapter(settings.ocr),
        ".tif": ImageReaderAdapter(settings.ocr),
        ".tiff": ImageReaderAdapter(settings.ocr),
        ".bmp": ImageReaderAdapter(settings.ocr),
        ".webp": ImageReaderAdapter(settings.ocr),
    }

    report_repo = ReportRepository(settings.paths.reports_dir)

    renderers = [
        HtmlRenderer(),
        DocxRenderer(),
        PptxRenderer(max_table_body_rows_per_slide=settings.pptx.max_table_body_rows_per_slide),
    ]

    # ---- SQL presets repository ----
    preset_repo = SqlServerPresetRepository(
        ini_path=str(resolved_ini),
        table_name="dbo.GapAnalysisPresets",
    )
    log.info("create_app: preset_repo=%s", type(preset_repo).__name__)

    # ---- Application service ----
    analysis_service = AnalysisService(
        settings=settings,
        llm=llm,
        fetcher=fetcher,
        readers=readers,
        report_repo=report_repo,
        md_normalizer=MarkdownNormalizer(),
        renderers=renderers,
        emailer=emailer,
    )

    return {"analysis_service": analysis_service, "preset_repo": preset_repo}


def create_processor_router(ini_path: str) -> ProcessorRouter:
    resolved_ini = _resolve_ini_path(ini_path)
    preset_repo = SqlServerPresetRepository(
        ini_path=str(resolved_ini),
        table_name="dbo.GapAnalysisPresets",
    )
    return ProcessorRouter(preset_repo=preset_repo)


def create_service() -> AnalysisService:
    return create_app()["analysis_service"]
