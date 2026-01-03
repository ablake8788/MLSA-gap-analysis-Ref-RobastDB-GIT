# llm.py                    # interface for LLM client

from __future__ import annotations
from typing import Protocol


class LlmClient(Protocol):
    def generate_report(self, *, model: str, prompt: str) -> str: ...
