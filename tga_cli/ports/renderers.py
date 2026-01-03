# renderers.py              # interface for report renderers

from __future__ import annotations
from typing import Protocol
from tga_cli.domain.models import RunContext, RunArtifacts


class ReportRenderer(Protocol):
    def render(self, *, report_md: str, ctx: RunContext, artifacts: RunArtifacts) -> None: ...

