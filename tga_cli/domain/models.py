from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

@dataclass(frozen=True)
class AppSettings:
    open_report: bool = False

@dataclass(frozen=True)
class Preset:
    """Domain model for a saved run preset."""
    id: int
    name: str
    competitor: str
    baseline: Optional[str]
    instruction_preset: Optional[str]
    extra_instructions: Optional[str]
    file: Optional[str]
    web: Optional[str]          # e.g. "1"/"0", "yes"/"no"
    processor: Optional[str]    # "local" | "web" | "hybrid"
    report_options: Optional[Dict[str, Any]] = None

@dataclass(frozen=True)
class Inputs:
    competitor: str
    baseline: str = ""
    instruction_preset: str = ""
    extra_instructions: str = ""
    file: str = ""
    preset_id: Optional[int] = None

@dataclass(frozen=True)
class RunInputs:
    competitor: str
    baseline: str = ""
    instruction_preset: str = ""
    extra_instructions: str = ""
    file: str = ""
    preset_id: Optional[int] = None

from typing import Optional, Dict, Any

@dataclass(frozen=True)
class CliArgs:
    preset_id: Optional[int] = None

    file: Optional[str] = None
    competitor: Optional[str] = None
    baseline: Optional[str] = None   # None = flag absent; "" = flag present but disable
    model: str = ""
    max_rows: int = 20

    instruction_preset: str = ""
    extra_instructions: str = ""

    report_options: Optional[Dict[str, Any]] = None


# class CliArgs:
#     file: Optional[str]
#     competitor: Optional[str]
#     baseline: Optional[str]   # None = flag absent; "" = flag present but disable
#     model: str
#     max_rows: int
#     instruction_preset: str = ""
#     extra_instructions: str = ""

@dataclass(frozen=True)
class RunArtifacts:
    run_dir: Path
    md_path: Path
    html_path: Path
    docx_path: Path
    pptx_path: Path

@dataclass(frozen=True)
class RunContext:
    competitor_url: str
    baseline_url: str
    baseline_enabled: bool
    input_file: Path
    generated_at: str
    report_base: str

    include_references: bool = True
    reference_format: Optional[str] = None

@dataclass(frozen=True)
class RunResult:
    # Final run outcome
    status: str                      # "ok" | "failed"
    context: Optional[RunContext] = None
    artifacts: Optional[RunArtifacts] = None
    message: str = ""

    # Analysis payload (optional depending on stage)
    mode: Optional[str] = None
    competitor: Optional[str] = None
    baseline: Optional[str] = None
    instruction_preset: Optional[str] = None
    extra_instructions: Optional[str] = None
    file: Optional[str] = None
    summary: Optional[str] = None
    analysis_context: Optional[Dict[str, Any]] = None




# # dataclasses: Inputs, Outputs, RunContext, Result
#
# # tga_cli/domain/models.py
# # dataclasses: CliArgs, RunArtifacts, RunContext, RunResult (and optionally AppSettings)
#
# from __future__ import annotations
# from dataclasses import dataclass
# from pathlib import Path
# from typing import Optional, Dict, Any
#
# @dataclass(frozen=True)
# class AppSettings:
#     open_report: bool = False
#
# #################################
# @dataclass(frozen=True)
# class Preset:
#     """Domain model for a saved run preset."""
#     id: int
#     name: str
#     competitor: str
#     baseline: Optional[str]
#     instruction_preset: Optional[str]
#     extra_instructions: Optional[str]
#     file: Optional[str]
#     web: Optional[str]          # e.g. "1"/"0", "yes"/"no"
#     processor: Optional[str]    # "local" | "web" | "hybrid"
#     report_options: Optional[Dict[str, Any]] = None
#
# @dataclass(frozen=True)
# class Inputs:
#     competitor: str
#     baseline: str = ""
#     instruction_preset: str = ""
#     extra_instructions: str = ""
#     file: str = ""
#     preset_id: Optional[int] = None
#
# @dataclass(frozen=True)
# class RunInputs:
#     competitor: str
#     baseline: str = ""
#     instruction_preset: str = ""
#     extra_instructions: str = ""
#     file: str = ""
#     preset_id: Optional[int] = None
#
#
# # @dataclass(frozen=True)
# # class RunResult:
# #     """Generic result object. Extend later with artifacts/paths."""
# #     mode: str
# #     competitor: str
# #     baseline: str
# #     instruction_preset: str
# #     extra_instructions: str
# #     file: str
# #     summary: str
# #     context: Dict[str, Any]
#
#
#
# @dataclass(frozen=True)
# class RunResult:
#     # Final run outcome
#     status: str                      # "ok" | "failed"
#     context: Optional["RunContext"] = None
#     artifacts: Optional["RunArtifacts"] = None
#     message: str = ""
#
#     # Analysis payload (optional depending on stage)
#     mode: Optional[str] = None
#     competitor: Optional[str] = None
#     baseline: Optional[str] = None
#     instruction_preset: Optional[str] = None
#     extra_instructions: Optional[str] = None
#     file: Optional[str] = None
#     summary: Optional[str] = None
#     analysis_context: Optional[Dict[str, Any]] = None
#
#
#
#
# #################################
#
# @dataclass(frozen=True)
# class CliArgs:
#     file: Optional[str]
#     competitor: Optional[str]
#     baseline: Optional[str]   # None = flag absent; "" = flag present but disable
#     model: str
#     max_rows: int
#
#     # NEW prompt controls
#     instruction_preset: str = ""
#     extra_instructions: str = ""
#
#
# @dataclass(frozen=True)
# class RunArtifacts:
#     run_dir: Path
#     md_path: Path
#     html_path: Path
#     docx_path: Path
#     pptx_path: Path
#
#
# @dataclass(frozen=True)
# class RunContext:
#     competitor_url: str
#     baseline_url: str
#     baseline_enabled: bool
#     input_file: Path
#     generated_at: str
#     report_base: str
#
#
# # @dataclass(frozen=True)
# # class RunResult:
# #     status: str  # "ok" | "failed"
# #     context: RunContext
# #     artifacts: RunArtifacts
# #     message: str = ""
#
