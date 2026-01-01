# presets.py
#
from __future__ import annotations
from typing import Protocol, Optional, List, Dict, Any
from tga_cli.domain.models import Preset


class PresetRepository(Protocol):
    """Port for preset retrieval. Implemented by infrastructure adapters."""
    def get_active_presets(self) -> List[Dict[str, Any]]:
        ...

    def get_preset(self, preset_id: int) -> Optional[Preset]:
        ...
