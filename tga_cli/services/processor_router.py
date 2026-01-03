from __future__ import annotations

from typing import Optional, Dict, Any

from tga_cli.domain.models import Preset, RunInputs, RunResult
from tga_cli.ports.presets import PresetRepository

def parse_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    v = str(value).strip().lower()
    return v in ("1", "true", "yes", "y", "on", "enabled")


def normalize_processor(value: Optional[str]) -> str:
    if not value:
        return "local"
    v = value.strip().lower()
    if v in ("web", "online"):
        return "web"
    if v in ("hybrid", "mixed"):
        return "hybrid"
    return "local"


class ProcessorRouter:
    """
    Application service that:
    - loads preset (via PresetRepository port)
    - applies preset defaults (only when inputs are blank)
    - routes to the configured execution pipeline (local/web/hybrid)

    NOTE: Replace stub implementations with your real analysis pipelines.
    """

    def __init__(self, preset_repo: PresetRepository):
        self.preset_repo = preset_repo

    def run(self, inputs: RunInputs) -> RunResult:
        preset: Optional[Preset] = None
        web_enabled = False
        mode = "local"

        competitor = inputs.competitor.strip()
        baseline = inputs.baseline.strip()
        instruction_preset = inputs.instruction_preset.strip()
        extra_instructions = inputs.extra_instructions.strip()
        file = inputs.file.strip()

        if inputs.preset_id is not None:
            preset = self.preset_repo.get_preset(inputs.preset_id)
            if preset is None:
                raise ValueError(f"Preset id {inputs.preset_id} not found or inactive")

            # Apply defaults only when blanks are supplied
            competitor = competitor or preset.competitor
            baseline = baseline or (preset.baseline or "")
            instruction_preset = instruction_preset or (preset.instruction_preset or "")
            extra_instructions = extra_instructions or (preset.extra_instructions or "")
            file = file or (preset.file or "")

            web_enabled = parse_bool(preset.web)
            mode = normalize_processor(preset.processor)

        if not competitor:
            raise ValueError("competitor is required")

        if mode == "web":
            result = self._run_web(competitor, baseline, instruction_preset, extra_instructions, file, web_enabled)
        elif mode == "hybrid":
            result = self._run_hybrid(competitor, baseline, instruction_preset, extra_instructions, file, web_enabled)
        else:
            result = self._run_local(competitor, baseline, instruction_preset, extra_instructions, file, web_enabled)

        context: Dict[str, Any] = {
            "preset_id": preset.id if preset else None,
            "preset_name": preset.name if preset else None,
            "processor": mode,
            "web_enabled": web_enabled,
        }

        return RunResult(
            mode=result["mode"],
            competitor=competitor,
            baseline=baseline,
            instruction_preset=instruction_preset,
            extra_instructions=extra_instructions,
            file=file,
            summary=result["summary"],
            context=context,
        )

    # ---- Stubs: swap these with real analysis flows ----
    def _run_local(self, competitor: str, baseline: str, instruction_preset: str,
                   extra_instructions: str, file: str, web_enabled: bool) -> Dict[str, Any]:
        return {"mode": "local", "summary": "Local processor executed (stub)."}

    def _run_web(self, competitor: str, baseline: str, instruction_preset: str,
                 extra_instructions: str, file: str, web_enabled: bool) -> Dict[str, Any]:
        if not web_enabled:
            return {"mode": "web", "summary": "Web processor requested but web is disabled by preset."}
        return {"mode": "web", "summary": "Web processor executed (stub)."}

    def _run_hybrid(self, competitor: str, baseline: str, instruction_preset: str,
                    extra_instructions: str, file: str, web_enabled: bool) -> Dict[str, Any]:
        return {"mode": "hybrid", "summary": "Hybrid processor executed (stub)."}
