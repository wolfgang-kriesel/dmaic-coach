# Knowledge base (swap zone)

This folder is the **retrieval corpus** for the coach. Everything here is plain
Markdown and is intentionally easy to replace with your own training notes.

## How retrieval uses these files
- Each file is split into chunks by Markdown heading (`#`, `##`, ...).
- Each chunk is embedded and stored in a local SQLite vector index (`kb.db`).
- The coach and the evaluator retrieve the most relevant chunks and **cite them**
  as `[<filename> › <heading>]`.

## How to replace with your own content
1. Drop your own `.md` files in this folder (or edit the existing ones). Keep
   meaningful headings — they become the citation anchors.
2. Re-index:
   ```bash
   make ingest
   ```
3. Run a session — citations now point at your material.

This `README.md` is ignored by the indexer; only the content files are indexed.
