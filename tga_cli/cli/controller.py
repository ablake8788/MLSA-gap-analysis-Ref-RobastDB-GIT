#############
## controller.py
from __future__ import annotations

import logging
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

from tga_cli.cli.args import parse_args
from tga_cli.domain.errors import FatalError, ValidationError

logger = logging.getLogger("tga_cli")


def open_path(path: Path) -> None:
    p = Path(path)
    if not p.exists():
        return

    try:
        if sys.platform.startswith("win"):
            os.startfile(str(p))  # noqa: S606 (Windows shell open)
        elif sys.platform == "darwin":
            subprocess.run(["open", str(p)], check=False)
        else:
            subprocess.run(["xdg-open", str(p)], check=False)
    except Exception:
        return


def main() -> int:
    args = parse_args()

    # Import inside function to avoid circular imports in PyInstaller onefile mode.
    from tga_cli.app_factory import create_service
    from tga_cli.config.ini_config import load_settings
    from tga_cli.logging.setup import resolve_ini_path

    # Preset repo (SQL Server)
    from tga_cli.adapters.sqlserver_presets import SqlServerPresetRepository  # adjust if needed

    svc = create_service()

    # Load INI settings
    ini_path = resolve_ini_path("MLSA_GapAnalysisRefDB.ini")
    settings = load_settings(ini_path)

    logger.warning("INI resolved to: %s (exists=%s)", ini_path, ini_path.exists())
    logger.warning("open_report=%s", getattr(settings, "open_report", None))

    # If preset_id is provided, hydrate args from SQL preset (WITHOUT mutating frozen args)
    preset_id = getattr(args, "preset_id", None)
    if preset_id:
        repo = SqlServerPresetRepository(str(ini_path))
        preset = repo.get_preset(int(preset_id))
        if not preset:
            raise ValidationError(f"Preset not found or inactive: preset_id={preset_id}")

        # Precedence rules: CLI wins if user explicitly provided a value
        new_competitor = args.competitor or preset.competitor

        # baseline:
        # - if flag absent (None), use preset baseline (or "")
        # - if user explicitly passed "", keep it disabled
        new_baseline = args.baseline
        if new_baseline is None:
            new_baseline = preset.baseline or ""

        # file
        new_file = args.file or (preset.file or None)

        # prompt controls
        new_instruction_preset = (args.instruction_preset or "").strip() or (preset.instruction_preset or "")
        new_extra_instructions = (args.extra_instructions or "").strip() or (preset.extra_instructions or "")

        # critical for references appendix
        new_report_options = preset.report_options or {}

        # Build a new immutable args object
        args = replace(
            args,
            competitor=new_competitor,
            baseline=new_baseline,
            file=new_file,
            instruction_preset=new_instruction_preset,
            extra_instructions=new_extra_instructions,
            report_options=new_report_options,
        )

        logger.info("Preset hydrated: id=%s name=%s", preset.id, preset.name)
        logger.info("Hydrated report_options=%s", getattr(args, "report_options", None))

    # Existing logging
    logger.info(
        "Prompt controls: preset=%r extra_len=%d",
        getattr(args, "instruction_preset", ""),
        len((getattr(args, "extra_instructions", "") or "").strip()),
    )

    try:
        result = svc.run(args)

        logger.info("Done. Run folder: %s", result.artifacts.run_dir)
        logger.warning(
            "Artifacts: docx=%s (exists=%s)",
            result.artifacts.docx_path,
            result.artifacts.docx_path.exists(),
        )

        if settings.open_report:
            open_path(result.artifacts.docx_path)

        return 0 if result.status == "ok" else 2

    except ValidationError as e:
        logger.error("Validation error: %s", e)
        return 2
    except FatalError as e:
        logger.error("Fatal error: %s", e)
        return 2
    except Exception:
        logger.exception("Unhandled error")
        return 2















#############
## controller.py
# from __future__ import annotations
#
# import logging
# import os
# import subprocess
# import sys
# from pathlib import Path
#
# from tga_cli.cli.args import parse_args
# from tga_cli.domain.errors import FatalError, ValidationError
#
# logger = logging.getLogger("tga_cli")
#
#
# def open_path(path: Path) -> None:
#     p = Path(path)
#     if not p.exists():
#         return
#
#     try:
#         if sys.platform.startswith("win"):
#             os.startfile(str(p))  # noqa: S606 (Windows shell open)
#         elif sys.platform == "darwin":
#             subprocess.run(["open", str(p)], check=False)
#         else:
#             subprocess.run(["xdg-open", str(p)], check=False)
#     except Exception:
#         return
#
#
# def main() -> int:
#     args = parse_args()
#
#     # Import inside function to avoid circular imports in PyInstaller onefile mode.
#     from tga_cli.app_factory import create_service
#     from tga_cli.config.ini_config import load_settings
#     from tga_cli.logging.setup import resolve_ini_path
#
#     # NEW: preset repo (SQL Server)
#     from tga_cli.adapters.sqlserver_presets import SqlServerPresetRepository  # adjust module path if different
#
#     svc = create_service()
#
#     # Load INI settings
#     ini_path = resolve_ini_path("TisGapAnalysisRef.ini")
#     settings = load_settings(ini_path)
#
#     logger.warning("INI resolved to: %s (exists=%s)", ini_path, ini_path.exists())
#     logger.warning("open_report=%s", getattr(settings, "open_report", None))
#
#     # NEW: If preset_id is provided, hydrate args from SQL preset
#     preset_id = getattr(args, "preset_id", None)
#     if preset_id:
#         repo = SqlServerPresetRepository(str(ini_path))
#         preset = repo.get_preset(int(preset_id))
#         if not preset:
#             raise ValidationError(f"Preset not found or inactive: preset_id={preset_id}")
#
#         # Precedence rules: CLI wins if user explicitly provided a value
#         # competitor
#         if not getattr(args, "competitor", None):
#             args.competitor = preset.competitor
#
#         # baseline: if flag absent (None), use preset. If user passed "" to disable, keep disabled.
#         if getattr(args, "baseline", None) is None:
#             args.baseline = preset.baseline or ""
#
#         # file
#         if not getattr(args, "file", None) and preset.file:
#             args.file = preset.file
#
#         # prompt controls
#         if not (getattr(args, "instruction_preset", "") or "").strip():
#             args.instruction_preset = preset.instruction_preset or ""
#
#         if not (getattr(args, "extra_instructions", "") or "").strip():
#             args.extra_instructions = preset.extra_instructions or ""
#
#         # *** critical for references appendix ***
#         args.report_options = preset.report_options or {}
#
#         logger.info("Preset hydrated: id=%s name=%s", preset.id, preset.name)
#         logger.info("Hydrated report_options=%s", args.report_options)
#
#     # Existing logging
#     logger.info(
#         "Prompt controls: preset=%r extra_len=%d",
#         getattr(args, "instruction_preset", ""),
#         len((getattr(args, "extra_instructions", "") or "").strip()),
#     )
#
#     try:
#         result = svc.run(args)
#
#         logger.info("Done. Run folder: %s", result.artifacts.run_dir)
#         logger.warning(
#             "Artifacts: docx=%s (exists=%s)",
#             result.artifacts.docx_path,
#             result.artifacts.docx_path.exists(),
#         )
#
#         if settings.open_report:
#             open_path(result.artifacts.docx_path)
#
#         return 0 if result.status == "ok" else 2
#
#     except ValidationError as e:
#         logger.error("Validation error: %s", e)
#         return 2
#     except FatalError as e:
#         logger.error("Fatal error: %s", e)
#         return 2
#     except Exception:
#         logger.exception("Unhandled error")
#         return 2


# from __future__ import annotations
#
# import logging
# import os
# import subprocess
# import sys
# from pathlib import Path
#
# from tga_cli.cli.args import parse_args
# from tga_cli.domain.errors import FatalError, ValidationError
#
# logger = logging.getLogger("tga_cli")
#
#
# def open_path(path: Path) -> None:
#     p = Path(path)
#     if not p.exists():
#         return
#
#     try:
#         if sys.platform.startswith("win"):
#             os.startfile(str(p))  # noqa: S606 (Windows shell open)
#         elif sys.platform == "darwin":
#             subprocess.run(["open", str(p)], check=False)
#         else:
#             subprocess.run(["xdg-open", str(p)], check=False)
#     except Exception:
#         # Do not crash the run if opening fails
#         return
#
#
# def main() -> int:
#     args = parse_args()
#
#     # Import inside function to avoid circular imports in PyInstaller onefile mode.
#     from tga_cli.app_factory import create_service
#     from tga_cli.config.ini_config import load_settings
#     from tga_cli.logging.setup import resolve_ini_path  # or wherever you put this helper
#
#     svc = create_service()
#
#     # Load INI settings
#     ini_path = resolve_ini_path("TisGapAnalysisRef.ini")
#     settings = load_settings(ini_path)
#
#     logger.warning("INI resolved to: %s (exists=%s)", ini_path, ini_path.exists())
#     logger.warning("open_report=%s", getattr(settings, "open_report", None))
#
#     # NEW: log prompt-control args so you can verify they are flowing
#     logger.info(
#         "Prompt controls: preset=%r extra_len=%d",
#         getattr(args, "instruction_preset", ""),
#         len((getattr(args, "extra_instructions", "") or "").strip()),
#     )
#
#     try:
#         # svc.run(args) is correct *if* your service takes CliArgs and internally uses:
#         # args.instruction_preset and args.extra_instructions.
#         # (Next step: update domain/models.CliArgs + services/prompt_builder.py.)
#         result = svc.run(args)
#
#         logger.info("Done. Run folder: %s", result.artifacts.run_dir)
#         logger.warning(
#             "Artifacts: docx=%s (exists=%s)",
#             result.artifacts.docx_path,
#             result.artifacts.docx_path.exists(),
#         )
#
#         # OPEN REPORT
#         if settings.open_report:
#             open_path(result.artifacts.docx_path)
#
#         return 0 if result.status == "ok" else 2
#
#     except ValidationError as e:
#         logger.error("Validation error: %s", e)
#         return 2
#     except FatalError as e:
#         logger.error("Fatal error: %s", e)
#         return 2
#     except Exception:
#         logger.exception("Unhandled error")
#         return 2


# from __future__ import annotations
#
# import logging
#
# from tga_cli.cli.args import parse_args
# from tga_cli.domain.errors import ValidationError, FatalError
# import os
# import sys
# import subprocess
# from pathlib import Path
#
#
# logger = logging.getLogger("tga_cli")
#
# def open_path(path: Path) -> None:
#     p = Path(path)
#     if not p.exists():
#         return
#
#     try:
#         if sys.platform.startswith("win"):
#             os.startfile(str(p))  # noqa: S606 (Windows shell open)
#         elif sys.platform == "darwin":
#             subprocess.run(["open", str(p)], check=False)
#         else:
#             subprocess.run(["xdg-open", str(p)], check=False)
#     except Exception:
#         # Do not crash the run if opening fails
#         return
#
# def main() -> int:
#     args = parse_args()
#
#     # Import inside function to avoid circular imports in PyInstaller onefile mode.
#     from tga_cli.app_factory import create_service
#     from tga_cli.config.ini_config import load_settings
#     from tga_cli.logging.setup import resolve_ini_path  # or wherever you put this helper
#     from tga_cli.adapters.opener_os import open_path    # you create this adapter
#
#     svc = create_service()
#
#     # Load INI settings
#     ini_path = resolve_ini_path("TisGapAnalysisRef.ini")
#     settings = load_settings(ini_path)
#
#     logger.warning("INI resolved to: %s (exists=%s)", ini_path, ini_path.exists())
#     logger.warning("open_report=%s", getattr(settings, "open_report", None))
#
#     try:
#         result = svc.run(args)
#         logger.info("Done. Run folder: %s", result.artifacts.run_dir)
#         logger.warning("Artifacts: docx=%s (exists=%s)", result.artifacts.docx_path,result.artifacts.docx_path.exists())
#
#         # OPEN REPORT (HERE)
#         if settings.open_report:
#             open_path(result.artifacts.docx_path)
#
#         return 0 if result.status == "ok" else 2
#
#     except ValidationError as e:
#         logger.error("Validation error: %s", e)
#         return 2
#     except FatalError as e:
#         logger.error("Fatal error: %s", e)
#         return 2
#     except Exception:
#         logger.exception("Unhandled error")
#         return 2
#
#
#
#
#
