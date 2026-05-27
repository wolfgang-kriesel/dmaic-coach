"""Minimal local vector store backed by a single SQLite file.

Embeddings are stored as float32 blobs; search loads them and does an exact
cosine top-k in numpy. The corpus is tiny (a curated KB), so this is fast,
portable, and needs no external vector database or server.
"""
from __future__ import annotations

import sqlite3
import numpy as np


class VectorStore:
    def __init__(self, path: str):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS chunks(
                   id INTEGER PRIMARY KEY,
                   source TEXT, heading TEXT, text TEXT,
                   dim INTEGER, embedding BLOB)"""
        )
        self.conn.commit()

    def clear(self):
        self.conn.execute("DELETE FROM chunks")
        self.conn.commit()

    def add(self, source, heading, text, vec):
        vec = np.asarray(vec, dtype=np.float32)
        self.conn.execute(
            "INSERT INTO chunks(source,heading,text,dim,embedding) VALUES(?,?,?,?,?)",
            (source, heading, text, int(vec.size), vec.tobytes()),
        )

    def commit(self):
        self.conn.commit()

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]

    def _load(self):
        rows = self.conn.execute(
            "SELECT source,heading,text,embedding FROM chunks"
        ).fetchall()
        metas, mats = [], []
        for source, heading, text, emb in rows:
            metas.append((source, heading, text))
            mats.append(np.frombuffer(emb, dtype=np.float32))
        mat = np.vstack(mats) if mats else np.zeros((0, 1), dtype=np.float32)
        return metas, mat

    def search(self, qvec, k=4):
        metas, mat = self._load()
        if mat.shape[0] == 0:
            return []
        qvec = np.asarray(qvec, dtype=np.float32)
        sims = mat @ qvec
        order = np.argsort(-sims)[:k]
        out = []
        for i in order:
            s, h, t = metas[int(i)]
            out.append({"source": s, "heading": h, "text": t,
                        "score": float(sims[int(i)])})
        return out
