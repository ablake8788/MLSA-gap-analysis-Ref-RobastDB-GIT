# report_repository.py  # ensure_reports_dir / ensure_run_dir / file naming
from __future__ import annotations

from pathlib import Path


class ReportRepository:
    def __init__(self, reports_base: Path):
        self.reports_base = reports_base
        self.reports_base.mkdir(parents=True, exist_ok=True)

    def ensure_run_dir(self, report_base: str) -> Path:
        run_dir = self.reports_base / report_base
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir
