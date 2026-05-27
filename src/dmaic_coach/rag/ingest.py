"""Chunk the knowledge base by Markdown heading, embed, and index into SQLite."""
from __future__ import annotations

import glob
import os
import re

from .store import VectorStore
from .embedder import get_embedder


def chunk_markdown(text: str):
    """Yield (heading, body) sections split on Markdown headings."""
    chunks, cur_head, cur = [], "(intro)", []

    def flush():
        body = "\n".join(cur).strip()
        if body:
            chunks.append((cur_head, body))

    for line in text.splitlines():
        if re.match(r"^#{1,6}\s+", line):
            flush()
            cur = []
            cur_head = re.sub(r"^#{1,6}\s+", "", line).strip()
        else:
            cur.append(line)
    flush()
    return chunks


def ingest(kb_dir, db_path, embedder=None):
    embedder = embedder or get_embedder()
    store = VectorStore(db_path)
    store.clear()

    texts, metas = [], []
    for path in sorted(glob.glob(os.path.join(str(kb_dir), "*.md"))):
        if os.path.basename(path).lower() == "readme.md":
            continue
        content = open(path, encoding="utf-8").read()
        for head, body in chunk_markdown(content):
            metas.append((os.path.basename(path), head))
            texts.append(f"{head}\n{body}")

    if texts:
        vecs = embedder.embed(texts)
        for (src, head), text, vec in zip(metas, texts, vecs):
            store.add(src, head, text, vec)
        store.commit()
    return store.count(), embedder.name


def main():
    from ..config import KB_DIR, DB_PATH, load_env
    load_env()
    n, name = ingest(KB_DIR, DB_PATH)
    print(f"Indexed {n} chunks from {KB_DIR} using '{name}' embedder -> {DB_PATH}")


if __name__ == "__main__":
    main()
