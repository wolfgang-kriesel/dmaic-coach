"""Rubric evaluator.

The grade is produced by deterministic Python grounded in (a) statistics verified
by the MCP tool and (b) citations retrieved from the knowledge base — not by an
LLM's opinion. That is the point: the agent evaluates the learner defensibly.
"""
from __future__ import annotations

import yaml

from ..rag.retriever import Retriever, citation


def _keyword_score(notes: str, keywords):
    text = (notes or "").lower()
    hits = [k for k in keywords if k.lower() in text]
    frac = len(hits) / max(1, len(keywords))
    if frac >= 0.5:
        score = 3
    elif frac >= 0.30:
        score = 2
    elif hits:
        score = 1
    else:
        score = 0
    return score, hits


class Evaluator:
    def __init__(self, rubric_path, db_path):
        self.rubric = yaml.safe_load(open(rubric_path, encoding="utf-8"))
        self.retriever = Retriever(db_path)

    def evaluate(self, submission: dict, verified: dict, stakeholder_claim: float):
        notes = submission.get("notes", "")
        results = []
        for c in self.rubric["criteria"]:
            auto = c["auto"]
            cite = self.retriever.top_citation(c["query"]) or ""
            score, just = self._score_one(auto, c, submission, notes, verified,
                                           stakeholder_claim)
            results.append({
                "id": c["id"], "title": c["title"], "score": score, "max": 3,
                "justification": just, "citation": cite,
            })
        total = sum(r["score"] for r in results)
        mx = 3 * len(results)
        return {"criteria": results, "total": total, "max": mx,
                "pct": round(100 * total / mx)}

    def _score_one(self, auto, c, submission, notes, verified, stakeholder_claim):
        if auto == "keyword":
            score, hits = _keyword_score(notes, c["keywords"])
            return score, (f"Addressed {len(hits)}/{len(c['keywords'])} expected "
                           f"elements: {', '.join(hits) if hits else 'none'}.")
        if auto == "capability":
            claimed = submission.get("ppk")
            true = verified["Ppk"]
            if claimed is None:
                return 0, "No Ppk value provided."
            diff = abs(claimed - true)
            score = 3 if diff <= 0.15 else 2 if diff <= 0.3 else 1 if diff <= 0.6 else 0
            return score, (f"Learner Ppk={claimed:.2f} vs verified Ppk={true:.2f} "
                           f"(|diff|={diff:.2f}).")
        if auto == "interpretation":
            learner = submission.get("capable")
            true = verified["capable_at_1_33"]
            if learner is None:
                return 0, "No capability verdict provided."
            if learner == true:
                return 3, (f"Correct verdict: {'capable' if true else 'not capable'} "
                           f"(verified Ppk={verified['Ppk']:.2f} vs 1.33 threshold).")
            return 0, (f"Incorrect verdict; verified says "
                       f"{'capable' if true else 'not capable'}.")
        if auto == "claim":
            challenged = submission.get("challenged_claim")
            claim_false = verified["Ppk"] < stakeholder_claim - 0.3
            if challenged and claim_false:
                return 3, (f"Correctly challenged the stakeholder's Ppk={stakeholder_claim} "
                           f"claim (verified {verified['Ppk']:.2f}).")
            if (not challenged) and claim_false:
                return 0, (f"Accepted an unsupported claim (stated Ppk={stakeholder_claim}, "
                           f"verified {verified['Ppk']:.2f}).")
            return 2, "Claim handling is consistent with the data."
        if auto == "sigma":
            claimed = submission.get("baseline_sigma")
            true = verified["baseline_sigma_level"]
            if claimed is None:
                return 0, "No baseline sigma provided."
            diff = abs(claimed - true)
            score = 3 if diff <= 0.3 else 2 if diff <= 0.6 else 1 if diff <= 1.0 else 0
            return score, (f"Learner sigma={claimed:.2f} vs verified {true:.2f} "
                           f"(|diff|={diff:.2f}).")
        return 0, "n/a"
