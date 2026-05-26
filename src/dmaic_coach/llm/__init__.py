"""LLM provider factory."""
from __future__ import annotations

import os
from .base import LLMProvider


def get_provider(name: str | None = None) -> LLMProvider:
    name = (name or os.getenv("LLM_PROVIDER", "mock")).lower()
    if name == "mock":
        from .mock import MockProvider
        return MockProvider()
    if name == "anthropic":
        from .anthropic import AnthropicProvider
        return AnthropicProvider()
    if name == "openai":
        from .openai import OpenAIProvider
        return OpenAIProvider()
    if name in ("grok", "xai"):
        from .grok import GrokProvider
        return GrokProvider()
    raise ValueError(f"Unknown LLM_PROVIDER: {name!r}")
