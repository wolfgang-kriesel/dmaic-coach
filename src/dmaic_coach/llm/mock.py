"""Deterministic provider: returns the composed draft unchanged. No API, no network."""
from __future__ import annotations

from .base import LLMProvider


class MockProvider(LLMProvider):
    name = "mock"

    def say(self, persona_system: str, draft: str) -> str:
        return draft
