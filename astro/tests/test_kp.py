"""Deterministic tests for the KP significator engine."""

import pytest

from engine.birth_data import BirthData
from engine.chart import compute_kp_chart
from engine.kp import KPAnalysis, kp_house_of


# Aries-lagna whole-sign owners, used to build a controlled analysis.
_OWNER = {1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
          7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"}


def _owned_by():
    owned = {}
    for h, lord in _OWNER.items():
        owned.setdefault(lord, []).append(h)
    return owned


def make_analysis():
    """A controlled KP analysis with known occupancy and star-lords."""
    planet_house = {"Sun": 1, "Moon": 7, "Mars": 4, "Mercury": 7, "Jupiter": 7,
                    "Venus": 10, "Saturn": 7, "Rahu": 7, "Ketu": 7}
    occupants = {h: [] for h in range(1, 13)}
    for p, h in planet_house.items():
        occupants[h].append(p)
    star_lord = {"Moon": "Sun", "Venus": "Mars", "Sun": "Jupiter", "Mars": "Saturn",
                 "Mercury": "Ketu", "Jupiter": "Rahu", "Saturn": "Mercury",
                 "Rahu": "Venus", "Ketu": "Moon"}
    sub_lord = {"Moon": "Sun", "Sun": "Sun", "Mars": "Mars", "Venus": "Mercury",
                "Mercury": "Mercury", "Jupiter": "Jupiter", "Saturn": "Saturn",
                "Rahu": "Rahu", "Ketu": "Ketu"}
    return KPAnalysis(
        planet_house=planet_house, occupants=occupants, owner=dict(_OWNER),
        star_lord=star_lord, sub_lord=sub_lord, houses_owned_by=_owned_by(),
        cuspal_sub_lord={h: "Jupiter" for h in range(1, 13)},
    )


# --------------------------------------------------------------------------- #
def test_kp_house_of_arc_logic():
    cusps = [i * 30.0 for i in range(12)]   # 0,30,...,330
    assert kp_house_of(5.0, cusps) == 1
    assert kp_house_of(35.0, cusps) == 2
    assert kp_house_of(359.0, cusps) == 12


def test_kp_house_of_wraps_when_cusps_not_zero_based():
    cusps = [340.0, 10.0, 40.0, 70.0, 100.0, 130.0, 160.0, 190.0,
             220.0, 250.0, 280.0, 310.0]
    assert kp_house_of(350.0, cusps) == 1     # 350 in [340, 10)
    assert kp_house_of(5.0, cusps) == 1       # wraps past 360
    assert kp_house_of(20.0, cusps) == 2


def test_house_significators_four_steps_ordered():
    A = make_analysis()
    sigs = A.house_significators(1)
    # L1 in-star-of-occupant(Sun)=Moon; L2 occupant Sun; L3 in-star-of-owner(Mars)=Venus; L4 owner Mars.
    assert [(s.planet, s.level) for s in sigs] == [
        ("Moon", 1), ("Sun", 2), ("Venus", 3), ("Mars", 4)]


def test_planet_significations_levels():
    A = make_analysis()
    sig = A.planet_significations("Moon")   # star-lord = Sun
    # Sun occupies house 1 (L1); Sun owns 5 (L2); Moon occupies 7 (L3); Moon owns 4 (L4).
    assert sig == {1: 1, 5: 2, 7: 3, 4: 4}


def test_final_significators_prunes_by_sublord():
    A = make_analysis()
    raw = A.significators_of_houses([1])
    final = A.final_significators([1])
    assert set(final) <= set(raw)
    # Venus' sub-lord is Mercury, which signifies {3,6,7} (not house 1) -> pruned.
    assert "Venus" in raw
    assert "Venus" not in final


@pytest.fixture
def kp_delhi():
    return compute_kp_chart(
        BirthData(1990, 1, 1, 12, 0, 0, 28.6139, 77.2090, "Asia/Kolkata"))


def test_house_placement_consistent_with_cusps(kp_delhi):
    A = KPAnalysis.from_chart(kp_delhi)
    cusps = [c.longitude for c in kp_delhi.cusps]

    def in_arc(x, s, e):
        span = (e - s) % 360 or 360
        return ((x - s) % 360) < span

    for name, p in kp_delhi.planets.items():
        h = A.planet_house[name]
        assert in_arc(p.longitude % 360, cusps[h - 1], cusps[h % 12])
