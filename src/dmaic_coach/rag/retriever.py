"""Retrieve cited knowledge-base passages for a query."""
from __future__ import annotations

from .store import VectorStore
from .embedder import get_embedder


def citation(result: dict) -> str:
    return f"[{result['source']} › {result['heading']}]"


class Retriever:
    def __init__(self, db_path, embedder=None):
        self.store = VectorStore(db_path)
        self.embedder = embedder or get_embedder()

    def query(self, text: str, k: int = 4):
        qv = self.embedder.embed([text])[0]
        return self.store.search(qv, k)

    def top_citation(self, text: str) -> str | None:
        hits = self.query(text, k=1)
        return citation(hits[0]) if hits else None
