import os
import tempfile

from dmaic_coach.config import KB_DIR
from dmaic_coach.rag.ingest import ingest
from dmaic_coach.rag.retriever import Retriever


def _index():
    db = os.path.join(tempfile.mkdtemp(), "kb.db")
    n, _ = ingest(KB_DIR, db)
    return db, n


def test_ingest_indexes_chunks():
    _, n = _index()
    assert n >= 10


def test_retrieval_routes_to_expected_sources():
    db, _ = _index()
    r = Retriever(db)
    cases = {
        "how to compute Ppk and is the process capable": "04-process-capability.md",
        "baseline sigma level and DPMO yield": "05-baseline-sigma-dpmo.md",
        "gage R&R repeatability reproducibility": "03-measurement-system-analysis.md",
        "operational definition sampling plan": "02-data-collection-plan.md",
    }
    for query, expected in cases.items():
        top = r.query(query, k=1)[0]
        assert top["source"] == expected, f"{query!r} -> {top['source']}"
        assert top["score"] > 0
