"""LLM provider interface.

Design note: correctness in this app does NOT depend on the LLM. Retrieval,
statistics and grading are deterministic Python. The provider is a thin *voice*
layer: given a persona system prompt and a fully-composed draft utterance, it
returns the text the user sees. The mock returns the draft verbatim (so the demo
is byte-for-byte reproducible); live providers may rephrase it in persona voice
while being instructed to preserve every fact, number and citation.
"""
from __future__ import annotations


class LLMProvider:
    name = "base"

    def say(self, persona_system: str, draft: str) -> str:
        raise NotImplementedError
