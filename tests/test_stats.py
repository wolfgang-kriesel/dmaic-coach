import math

from dmaic_coach.tools.stats import (
    descriptive_stats, process_capability, dpmo_sigma,
)


def test_descriptive_basic():
    d = [2, 4, 4, 4, 5, 5, 7, 9]
    s = descriptive_stats(d)
    assert s["n"] == 8
    assert s["mean"] == 5.0
    assert math.isclose(s["std"], 2.138, abs_tol=1e-3)


def test_capability_offcenter_ppk():
    # mean 5, sd ~2.138, spec [0,10] -> symmetric, Ppk == Pp
    d = [2, 4, 4, 4, 5, 5, 7, 9]
    c = process_capability(d, lsl=0, usl=10)
    assert math.isclose(c["Ppk"], 0.7795, abs_tol=1e-3)
    assert c["capable_at_1_33"] is False
    assert "Cp/Cpk would require" in c["assumption"]


def test_capability_picks_min_side():
    # off-center high -> upper side is the binding (smaller) Ppk
    d = [8, 9, 9, 10, 10, 10, 11, 11]
    c = process_capability(d, lsl=0, usl=12)
    assert c["Ppu"] < c["Ppl"]
    assert math.isclose(c["Ppk"], c["Ppu"], abs_tol=1e-9)


def test_dpmo_six_sigma_is_3_4():
    r = dpmo_sigma(3.4, 1_000_000)
    assert math.isclose(r["dpmo"], 3.4, abs_tol=1e-6)
    assert math.isclose(r["sigma_level"], 6.0, abs_tol=0.05)


def test_dpmo_three_sigma():
    # ~66,800 DPMO is the classic 3-sigma figure
    r = dpmo_sigma(66_800, 1_000_000)
    assert math.isclose(r["sigma_level"], 3.0, abs_tol=0.05)
