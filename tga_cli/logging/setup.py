# logging /
# __init__.py
# setup.py  # setup_logging + resource_path

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path


def resolve_ini_path(filename: str) -> Path:
    """Prefer INI next to EXE when frozen; else next to project root."""
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        p = exe_dir / filename
        if p.exists():
            return p

        meipass = Path(getattr(sys, "_MEIPASS", exe_dir))
        p2 = meipass / filename
        if p2.exists():
            return p2

        return p

    # Not frozen: project_root/<filename>
    return Path(__file__).resolve().parents[2] / filename


def resource_path(relative_path: str) -> Path:
    # For non-frozen usage this is just relative to CWD; for frozen, next to executable.
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / relative_path
    return Path.cwd() / relative_path


def setup_logging(level: str = "INFO") -> Path:
    log_base = resource_path("logs")
    log_base.mkdir(parents=True, exist_ok=True)

    date_dir = log_base / datetime.now().strftime("%Y%m%d")
    date_dir.mkdir(parents=True, exist_ok=True)

    log_file = date_dir / "TitaniumTechnologyGapAnalysisRef.log"

    lvl = getattr(logging, (level or "INFO").upper(), logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    fh = logging.FileHandler(log_file, encoding="utf-8")

    ch.setFormatter(fmt)
    fh.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(lvl)
    root.handlers.clear()
    root.addHandler(ch)
    root.addHandler(fh)

    logging.getLogger("tga_cli").info("Logging initialized: %s", log_file)
    return log_file
