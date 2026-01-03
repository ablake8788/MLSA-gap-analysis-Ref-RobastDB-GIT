# llm_openai.py             # OpenAI

from __future__ import annotations

import logging
from openai import OpenAI

from tga_cli.domain.errors import FatalError

logger = logging.getLogger("tga_cli")


class OpenAILlmClient:
    def __init__(self, *, api_key: str, model: str):
        self._client = OpenAI(api_key=api_key)
        self._default_model = model

    def generate_report(self, *, model: str, prompt: str) -> str:
        use_model = model or self._default_model
        try:
            resp = self._client.responses.create(
                model=use_model,
                input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
            )
        except Exception as e:
            raise FatalError(f"OpenAI request failed: {e}") from e

        out: list[str] = []
        try:
            for item in resp.output:
                if item.type == "message":
                    for c in item.content:
                        if c.type in ("output_text", "text"):
                            out.append(c.text)
        except Exception as e:
            raise FatalError(f"Unexpected OpenAI response format: {e}") from e

        text = "\n".join(out).strip()
        if not text:
            raise FatalError("OpenAI returned an empty report.")
        return text
