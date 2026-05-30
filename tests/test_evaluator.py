from dmaic_coach.config import RUBRIC, KB_DIR
from dmaic_coach.rag.ingest import ingest
from dmaic_coach.agent.evaluator import Evaluator

import os
import tempfile

VERIFIED = {
    "Ppk": 0.64, "capable_at_1_33": False, "baseline_sigma_level": 3.14,
}
CLAIM = 1.5


def _evaluator():
    db = os.path.join(tempfile.mkdtemp(), "kb.db")
    ingest(KB_DIR, db)
    return Evaluator(RUBRIC, db)


def test_strong_submission_scores_high():
    ev = _evaluator()
    sub = {
        "ppk": 0.6, "capable": False, "baseline_sigma": 3.1,
        "challenged_claim": True,
        "notes": ("data collection plan with operational definitions, sampling "
                  "across operators and shifts; flagged gage / measurement system risk"),
    }
    rep = ev.evaluate(sub, VERIFIED, CLAIM)
    assert rep["pct"] >= 85
    # every criterion carries a citation
    assert all(r["citation"].startswith("[") for r in rep["criteria"])


def test_accepting_false_claim_is_penalised():
    ev = _evaluator()
    sub = {
        "ppk": 1.5, "capable": True, "baseline_sigma": 5.0,
        "challenged_claim": False, "notes": "looks fine to me",
    }
    rep = ev.evaluate(sub, VERIFIED, CLAIM)
    by_id = {r["id"]: r for r in rep["criteria"]}
    assert by_id["stakeholder_challenge"]["score"] == 0
    assert by_id["interpretation"]["score"] == 0
    assert by_id["capability_calc"]["score"] == 0
    assert rep["pct"] < 50
