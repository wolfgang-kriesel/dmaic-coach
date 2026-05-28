"""Optional Anthropic (Claude) voice provider."""
from __future__ import annotations

import os
from .base import LLMProvider

_INSTRUCTION = (
    "Rephrase the following message in your persona's voice. Preserve every "
    "fact, number, threshold and bracketed [citation] exactly. Do not add new "
    "claims.\n\nMESSAGE:\n"
)


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, model: str = "claude-sonnet-4-6"):
        import anthropic
        self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self._model = model

    def say(self, persona_system: str, draft: str) -> str:
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=persona_system,
            messages=[{"role": "user", "content": _INSTRUCTION + draft}],
        )
        return msg.content[0].text
