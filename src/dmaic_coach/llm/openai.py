"""Optional OpenAI (GPT) voice provider."""
from __future__ import annotations

import os
from .base import LLMProvider
from .anthropic import _INSTRUCTION


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, model: str = "gpt-4o"):
        from openai import OpenAI
        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
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
