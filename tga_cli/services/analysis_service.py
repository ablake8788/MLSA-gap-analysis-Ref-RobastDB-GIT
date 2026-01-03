from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from tga_cli.config.ini_config import AppSettings
from tga_cli.domain.errors import ValidationError
from tga_cli.domain.models import CliArgs, RunArtifacts, RunContext, RunResult

from tga_cli.services.baseline_policy import choose_baseline, is_blank_baseline
from tga_cli.services.prompt_builder import build_prompt
from tga_cli.services.url_normalizer import validate_http_url

from tga_cli.utils.text import truncate, build_report_base_name

logger = logging.getLogger("tga_cli")


class AnalysisService:
    def __init__(
        self,
        *,
        settings: AppSettings,
        llm,
        fetcher,
        readers: Dict[str, object],
        report_repo,
        md_normalizer,
        renderers,
        emailer=None,
    ):
        self.settings = settings
        self.llm = llm
        self.fetcher = fetcher
        self.readers = readers
        self.report_repo = report_repo
        self.md_normalizer = md_normalizer
        self.renderers = renderers
        self.emailer = emailer

    @staticmethod
    def _append_references_appendix_if_enabled(
        *,
        report_md: str,
        competitor_url: str,
        baseline_url: str,
        baseline_enabled: bool,
        input_file: Path,
        generated_at: str,
        report_options: Dict[str, Any] | None,
    ) -> str:
        opts = report_options or {}
        include_references = bool(opts.get("include_references", True))
        reference_format = str(opts.get("reference_format", "appendix") or "appendix")
        citation_level = str(opts.get("citation_level", "section") or "section")

        if not include_references:
            return report_md

        if reference_format.lower() != "appendix":
            return report_md

        appendix_lines = [
            "\n## Appendix A — Reference Sources\n",
            f"- Generated at: {generated_at}\n",
            f"- Citation level: {citation_level}\n",
            f"- Primary competitor (web): {competitor_url}\n",
        ]
        if baseline_enabled and baseline_url:
            appendix_lines.append(f"- Baseline / secondary comparator (web): {baseline_url}\n")
        appendix_lines.append(f"- Reference document (file): {str(input_file)}\n")

        return report_md + "".join(appendix_lines)

    @staticmethod
    def _prompt_competitor_if_needed(competitor_raw: str | None) -> str:
        if competitor_raw and competitor_raw.strip():
            return competitor_raw.strip()

        if not sys.stdin or not sys.stdin.isatty():
            raise ValidationError("Missing --competitor and cannot prompt (stdin not available).")

        entered = input("Enter competitor URL (e.g., https://example.com): ").strip()
        while not entered:
            entered = input("Enter competitor URL (e.g., https://example.com): ").strip()
        return entered

    def _resolve_input_file(self, file_arg: str | None) -> Path:
        if file_arg and str(file_arg).strip():
            p = Path(str(file_arg).strip())
            if not p.is_absolute():
                p = (self.settings.paths.compare_dir / p)
            p = p.resolve(strict=False)
            return self._validate_file(p)

        compare_dir = self.settings.paths.compare_dir
        exts = {".pdf", ".docx", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}
        candidates = [p for p in compare_dir.rglob("*") if p.is_file() and p.suffix.lower() in exts]
        if not candidates:
            raise ValidationError("No supported input files found; provide --file or populate compare_file_location.")

        newest = max(candidates, key=lambda p: p.stat().st_mtime)
        return self._validate_file(newest.resolve(strict=False))

    @staticmethod
    def _validate_file(fp: Path) -> Path:
        if not fp.exists():
            raise ValidationError(f"Input file not found: {fp}")
        if not fp.is_file():
            raise ValidationError(f"Input path is not a file: {fp}")
        allowed = {".pdf", ".docx", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}
        if fp.suffix.lower() not in allowed:
            raise ValidationError(f"Unsupported file type '{fp.suffix}'. Supported: {', '.join(sorted(allowed))}")
        return fp

    def run(self, args: CliArgs) -> RunResult:
        s = self.settings
        model = (args.model or "").strip() or s.openai.model

        competitor_raw = self._prompt_competitor_if_needed(args.competitor)
        competitor_url = validate_http_url(competitor_raw, "Competitor")

        baseline_candidate = choose_baseline(args.baseline, s.settings.baseline_url)
        if is_blank_baseline(baseline_candidate):
            baseline_enabled = False
            baseline_url = ""
        else:
            baseline_enabled = True
            baseline_url = validate_http_url(baseline_candidate, "Baseline")

        input_file = self._resolve_input_file(args.file)
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_base = build_report_base_name(competitor_url)

        run_dir = self.report_repo.ensure_run_dir(report_base)
        artifacts = RunArtifacts(
            run_dir=run_dir,
            md_path=run_dir / f"{report_base}.md",
            html_path=run_dir / f"{report_base}.html",
            docx_path=run_dir / f"{report_base}.docx",
            pptx_path=run_dir / f"{report_base}.pptx",
        )

        ext = input_file.suffix.lower()
        reader = self.readers.get(ext)
        if not reader:
            raise ValidationError(f"No reader configured for file type: {ext}")

        logger.info("Reading document: %s", input_file)
        doc_text = truncate(reader.read(input_file), s.settings.max_doc_chars)  # type: ignore[attr-defined]

        logger.info("Fetching competitor: %s", competitor_url)
        comp_text = truncate(self.fetcher.fetch_text(competitor_url), s.settings.max_site_chars)

        base_text = ""
        if baseline_enabled:
            logger.info("Fetching baseline: %s", baseline_url)
            base_text = truncate(self.fetcher.fetch_text(baseline_url), s.settings.max_site_chars)
        else:
            logger.info("Baseline disabled.")

        prompt = build_prompt(doc_text, comp_text, base_text, competitor_url, baseline_url)

        logger.info("Calling LLM (model=%s)...", model)
        logger.info("FINAL AI PROMPT START")
        logger.info(prompt)
        logger.info("FINAL AI PROMPT END")

        report_md = self.llm.generate_report(model=model, prompt=prompt)  # type: ignore[attr-defined]

        header = (
            "# Competitor Gap Analysis\n"
            f"- Primary Competitor: {competitor_url}\n"
        )
        if baseline_enabled:
            header += f"- Secondary Competitor: {baseline_url}\n"
        header += f"- Generated: {generated_at}\n- Input file: {input_file.name}\n\n"

        # If you want normalization, re-enable this:
        # report_md = self.md_normalizer.normalize(header + report_md)  # type: ignore[attr-defined]
        report_md = header + report_md

        report_md = self._append_references_appendix_if_enabled(
            report_md=report_md,
            competitor_url=competitor_url,
            baseline_url=baseline_url,
            baseline_enabled=baseline_enabled,
            input_file=input_file,
            generated_at=generated_at,
            report_options={"include_references": True, "reference_format": "appendix", "citation_level": "section"},
        )

        artifacts.md_path.write_text(report_md, encoding="utf-8")

        ctx = RunContext(
            competitor_url=competitor_url,
            baseline_url=baseline_url,
            baseline_enabled=baseline_enabled,
            input_file=input_file,
            generated_at=generated_at,
            report_base=report_base,
        )

        for r in self.renderers:
            r.render(report_md=report_md, ctx=ctx, artifacts=artifacts)  # type: ignore[attr-defined]

        if self.emailer:
            try:
                self.emailer.send([artifacts.md_path, artifacts.html_path, artifacts.docx_path, artifacts.pptx_path])
            except Exception:
                logger.exception("Email failed (continuing).")

        return RunResult(status="ok", context=ctx, artifacts=artifacts, message="Success")
