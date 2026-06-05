"""Deterministic tests for Ashtakavarga.

Structural invariants plus a regression on the Delhi chart's Sarvashtakavarga
(values cross-checked against PyJHora / Jagannatha Hora).
"""

import pytest

from engine.ashtakavarga import (
    AV_PLANETS,
    BENEFIC_HOUSES,
    bhinnashtakavarga,
    by_house,
    sarvashtakavarga,
)
from engine.birth_data import BirthData
from engine.chart import compute_vedic_chart

PLANET_TOTALS = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
                 "Jupiter": 56, "Venus": 52, "Saturn": 39}


@pytest.fixture
def delhi():
    return compute_vedic_chart(
        BirthData(1990, 1, 1, 12, 0, 0, 28.6139, 77.2090, "Asia/Kolkata"))


def test_benefic_table_totals_are_canonical():
    for planet, total in PLANET_TOTALS.items():
        got = sum(len(houses) for houses in BENEFIC_HOUSES[planet].values())
        assert got == total, f"{planet} table sums to {got}, expected {total}"


def test_bhinna_totals(delhi):
    bav = bhinnashtakavarga(delhi)
    for planet, total in PLANET_TOTALS.items():
        assert sum(bav[planet]) == total


def test_sarva_totals_337(delhi):
    sav = sarvashtakavarga(delhi)
    assert sum(sav) == 337
    assert len(sav) == 12


def test_sarva_regression_delhi(delhi):
    # Cross-checked against PyJHora (Jagannatha Hora), by sign Aries..Pisces.
    assert sarvashtakavarga(delhi) == [29, 30, 30, 24, 27, 30, 31, 29, 32, 25, 21, 29]


def test_by_house_repartitions_without_loss(delhi):
    sav = sarvashtakavarga(delhi)
    asc_sign = int(delhi.ascendant // 30)
    houses = by_house(sav, asc_sign)
    assert set(houses) == set(range(1, 13))
    assert sum(houses.values()) == 337
