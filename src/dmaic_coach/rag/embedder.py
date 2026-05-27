"""Pluggable embeddings.

Default backend is a dependency-free, deterministic hashing embedder: it needs no
model download and no network, so the whole RAG pipeline runs offline and gives
identical results every run (important for a reproducible demo and for tests).
Set EMBEDDER=fastembed for higher-quality neural embeddings (optional extra).
"""
from __future__ import annotations

import hashlib
import os
import re
import numpy as np

_DIM = 256


def _tokens(text: str):
    text = text.lower()
    for w in re.findall(r"[a-z0-9]+", text):
        yield w
        padded = f"#{w}#"
        for i in range(len(padded) - 2):
            yield padded[i:i + 3]  # character trigrams for subword robustness


class HashingEmbedder:
    name = "local-hashing"
    dim = _DIM

    def embed(self, texts):
        vecs = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            for tok in _tokens(t):
                h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
                idx = h % self.dim
                sign = 1.0 if (h >> 8) & 1 == 0 else -1.0
                vecs[i, idx] += sign
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vecs / norms


class FastEmbedEmbedder:
    name = "fastembed"

    def __init__(self, model="BAAI/bge-small-en-v1.5"):
        from fastembed import TextEmbedding
        self._m = TextEmbedding(model_name=model)
        self.dim = None

    def embed(self, texts):
        vecs = np.array(list(self._m.embed(list(texts))), dtype=np.float32)
        self.dim = vecs.shape[1]
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vecs / norms


def get_embedder(name: str | None = None):
    name = (name or os.getenv("EMBEDDER", "local")).lower()
    if name in ("fastembed", "neural"):
        return FastEmbedEmbedder()
    return HashingEmbedder()
