"""Pure statistical functions for the Measure phase.

These are deliberately dependency-light (numpy + scipy) and side-effect free so
they can be unit-tested directly and exposed unchanged through the MCP server.
The agent never trusts the learner's numbers; it calls these to verify them.
"""
from __future__ import annotations

from typing import Optional
import numpy as np
from scipy import stats as sstats


def _f(x: Optional[float]) -> Optional[float]:
    return None if x is None else float(x)


def descriptive_stats(data) -> dict:
    """Basic descriptive statistics for a sample of individual measurements."""
    a = np.asarray(data, dtype=float)
    if a.size == 0:
        raise ValueError("data is empty")
    return {
        "n": int(a.size),
        "mean": float(a.mean()),
        "std": float(a.std(ddof=1)) if a.size > 1 else 0.0,
        "min": float(a.min()),
        "max": float(a.max()),
        "median": float(np.median(a)),
    }


def process_capability(data, lsl=None, usl=None, target=None) -> dict:
    """Overall process capability (Pp / Ppk) for ungrouped individual data.

    With ungrouped individuals there are no rational subgroups, so only the
    overall (long-term) standard deviation is available. We therefore report
    Pp/Ppk and flag the assumption — Cp/Cpk would require subgrouped data.
    """
    a = np.asarray(data, dtype=float)
    if a.size < 2:
        raise ValueError("need at least 2 measurements for capability")
    mu = float(a.mean())
    sd = float(a.std(ddof=1))

    pp = ppu = ppl = ppk = None
    if usl is not None and lsl is not None:
        pp = (usl - lsl) / (6 * sd)
    if usl is not None:
        ppu = (usl - mu) / (3 * sd)
    if lsl is not None:
        ppl = (mu - lsl) / (3 * sd)
    sided = [x for x in (ppu, ppl) if x is not None]
    if sided:
        ppk = min(sided)

    ppm = None
    if usl is not None or lsl is not None:
        p_above = float(1 - sstats.norm.cdf(usl, mu, sd)) if usl is not None else 0.0
        p_below = float(sstats.norm.cdf(lsl, mu, sd)) if lsl is not None else 0.0
        ppm = (p_above + p_below) * 1e6

    capable = None if ppk is None else bool(ppk >= 1.33)
    return {
        "n": int(a.size),
        "mean": mu,
        "std": sd,
        "Pp": _f(pp),
        "Ppk": _f(ppk),
        "Ppu": _f(ppu),
        "Ppl": _f(ppl),
        "expected_ppm_out_of_spec": _f(ppm),
        "capable_at_1_33": capable,
        "assumption": "Ungrouped individuals: overall sigma used (Pp/Ppk). "
                      "Cp/Cpk would require rational subgroups.",
    }


def dpmo_sigma(defects: float, units: float, opportunities: float = 1) -> dict:
    """DPMO and process sigma level (with the conventional 1.5 sigma shift)."""
    if units <= 0 or opportunities <= 0:
        raise ValueError("units and opportunities must be positive")
    dpmo = (defects / (units * opportunities)) * 1e6
    y = 1 - dpmo / 1e6
    if y <= 0:
        z = 0.0
    elif y >= 1:
        z = 6.0
    else:
        z = float(sstats.norm.ppf(y))
    return {
        "dpmo": float(dpmo),
        "yield": float(max(0.0, min(1.0, y))),
        "sigma_level": float(z + 1.5),
    }
