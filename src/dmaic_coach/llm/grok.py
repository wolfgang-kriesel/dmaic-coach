"""Optional xAI (Grok) voice provider. Uses the OpenAI-compatible endpoint."""
from __future__ import annotations

import os
from .base import LLMProvider
from .anthropic import _INSTRUCTION


class GrokProvider(LLMProvider):
    name = "grok"

    def __init__(self, model: str = "grok-2-latest"):
        from openai import OpenAI
        self._client = OpenAI(
            api_key=os.environ["XAI_API_KEY"],
            base_url="https://api.x.ai/v1",
        )
        self._model = model

    def say(self, persona_system: str, draft: str) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": persona_system},
                {"role": "user", "content": _INSTRUCTION + draft},
            ],
        )
        return resp.choices[0].message.content
