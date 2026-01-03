# cli/args.py  (argparse only)

from __future__ import annotations

import argparse

from tga_cli.domain.models import CliArgs


def parse_args(argv=None) -> CliArgs:
    ap = argparse.ArgumentParser()

    ap.add_argument("--file", required=False, help="Input company document (PDF/DOCX/image).")
    ap.add_argument("--competitor", required=False, help="Competitor URL. If omitted, prompts when interactive.")
    ap.add_argument("--preset-id", dest="preset_id", type=int, default=None,
                    help="Preset ID from dbo.GapAnalysisPresets.")

    # Optional value handling:
    # --baseline            -> disables baseline
    # --baseline ""         -> disables baseline
    # --baseline https://x  -> enables baseline
    # flag absent -> None (fallback to INI)
    ap.add_argument("--baseline", nargs="?", const="", default=None, help="Baseline URL (defaults from INI).")

    ap.add_argument("--model", default="", help="OpenAI model override (optional).")
    ap.add_argument("--max-rows", dest="max_rows", type=int, default=20, help="Max table body rows per slide.")

    # Prompt controls
    ap.add_argument(
        "--instruction-preset",
        dest="instruction_preset",
        default="",
        help="Preset instruction profile key (e.g., scoring, executive, technical, evidence_strict, slide, risk).",
    )
    ap.add_argument(
        "--extra-instructions",
        dest="extra_instructions",
        default="",
        help="Additional free-text instructions appended to the prompt.",
    )

    ns = ap.parse_args(argv)

    return CliArgs(
        preset_id=ns.preset_id,
        file=ns.file,
        competitor=ns.competitor,
        baseline=ns.baseline,
        model=ns.model,
        max_rows=ns.max_rows,
        instruction_preset=ns.instruction_preset,
        extra_instructions=ns.extra_instructions,
        report_options=None,  # hydrated from DB in controller when preset_id is used
    )











# # cli/args.py  (argparse only)
#
# from __future__ import annotations
#
# import argparse
#
# from tga_cli.domain.models import CliArgs
#
#
# def parse_args(argv=None) -> CliArgs:
#     ap = argparse.ArgumentParser()
#
#     ap.add_argument("--file", required=False, help="Input company document (PDF/DOCX/image).")
#     ap.add_argument("--competitor", required=False, help="Competitor URL. If omitted, prompts when interactive.")
#
#     # Optional value handling:
#     # --baseline            -> disables baseline
#     # --baseline ""         -> disables baseline
#     # --baseline https://x  -> enables baseline
#     # flag absent -> None (fallback to INI)
#     ap.add_argument("--baseline", nargs="?", const="", default=None, help="Baseline URL (defaults from INI).")
#
#     ap.add_argument("--model", default="", help="OpenAI model override (optional).")
#     ap.add_argument("--max-rows", dest="max_rows", type=int, default=20, help="Max table body rows per slide.")
#
#     # NEW: prompt controls (web UI + CLI)
#     ap.add_argument(
#         "--instruction-preset",
#         dest="instruction_preset",
#         default="",
#         help="Preset instruction profile key (e.g., scoring, executive, technical, evidence_strict, slide, risk).",
#     )
#     ap.add_argument(
#         "--extra-instructions",
#         dest="extra_instructions",
#         default="",
#         help="Additional free-text instructions appended to the prompt.",
#     )
#
#     ns = ap.parse_args(argv)
#
#     return CliArgs(
#         file=ns.file,
#         competitor=ns.competitor,
#         baseline=ns.baseline,
#         model=ns.model,
#         max_rows=ns.max_rows,
#         instruction_preset=ns.instruction_preset,
#         extra_instructions=ns.extra_instructions,
#     )
#
#





# # cli/
# #       __init__.py
# #       args.py                   # argparse only
# #       controller.py             # calls service, handles exit codes/logging
#
# from __future__ import annotations
# import argparse
# from tga_cli.domain.models import CliArgs
#
#
# def parse_args(argv=None) -> CliArgs:
#     ap = argparse.ArgumentParser()
#
#     ap.add_argument("--file", required=False, help="Input company document (PDF/DOCX/image).")
#     ap.add_argument("--competitor", required=False, help="Competitor URL. If omitted, prompts when interactive.")
#
#     # Optional value handling:
#     # --baseline            -> disables baseline
#     # --baseline ""         -> disables baseline
#     # --baseline https://x  -> enables baseline
#     # flag absent -> None (fallback to INI)
#     ap.add_argument("--baseline", nargs="?", const="", default=None, help="Baseline URL (defaults from INI).")
#
#     ap.add_argument("--model", default="", help="OpenAI model override (optional).")
#     ap.add_argument("--max-rows", dest="max_rows", type=int, default=20, help="Max table body rows per slide.")
#
#     ns = ap.parse_args(argv)
#
#     return CliArgs(
#         file=ns.file,
#         competitor=ns.competitor,
#         baseline=ns.baseline,
#         model=ns.model,
#         max_rows=ns.max_rows,
#     )
