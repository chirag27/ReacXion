"""Golden-chart validation against Jagannatha Hora (and a KP tool for subs).

Each chart is cast twice — Vedic (Lahiri + whole-sign) and KP (KP ayanamsa +
Placidus). Assertions that have no reference value yet are skipped, so this
file is green from day one and tightens automatically as you fill
``golden_charts.py`` from JHora.

Tolerance: ARCMINUTE (1/60 degree) on every longitude and cusp, per the
validation requirement.
"""

import pytest

from engine.chart import compute_chart
from engine.constants import PRESET_KP, PRESET_VEDIC
from engine.dasha import balance_at_birth
from engine.varga import divisional_chart

from tests.golden_charts import GOLDEN_CHARTS, ExpectedChart, GoldenChart

ARCMINUTE = 1.0 / 60.0
DASHA_YEAR_TOL = 0.01   # years (~3.7 days) on the balance-at-birth


def angular_diff(a: float, b: float) -> float:
    """Smallest absolute difference between two angles, in degrees [0, 180]."""
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)


def _has_any_expectation(exp: ExpectedChart) -> bool:
    return any(
        v is not None
        for v in (
            exp.planet_longitudes,
            exp.planet_nakshatra_pada,
            exp.planet_sublords,
            exp.ascendant,
            exp.cusps,
            exp.cusp_sublords,
        )
    )


def _check(chart, exp: ExpectedChart, label: str):
    checked = 0

    if exp.planet_longitudes:
        for name, expected_lon in exp.planet_longitudes.items():
            actual = chart.planets[name].longitude
            diff = angular_diff(actual, expected_lon)
            assert diff <= ARCMINUTE, (
                f"[{label}] {name} longitude {actual:.6f}° vs expected "
                f"{expected_lon:.6f}° -> {diff * 60:.3f}' off"
            )
            checked += 1

    if exp.planet_nakshatra_pada:
        for name, (nak, pada) in exp.planet_nakshatra_pada.items():
            p = chart.planets[name]
            assert (p.nakshatra, p.pada) == (nak, pada), (
                f"[{label}] {name} nakshatra/pada {(p.nakshatra, p.pada)} "
                f"vs expected {(nak, pada)}"
            )
            checked += 1

    if exp.planet_sublords:
        for name, sub in exp.planet_sublords.items():
            actual = chart.planets[name].sub_lord
            assert actual == sub, (
                f"[{label}] {name} sub-lord {actual} vs expected {sub}"
            )
            checked += 1

    if exp.ascendant is not None:
        diff = angular_diff(chart.ascendant, exp.ascendant)
        assert diff <= ARCMINUTE, (
            f"[{label}] ascendant {chart.ascendant:.6f}° vs expected "
            f"{exp.ascendant:.6f}° -> {diff * 60:.3f}' off"
        )
        checked += 1

    if exp.cusps:
        for house, expected_lon in exp.cusps.items():
            actual = chart.cusps[house - 1].longitude
            diff = angular_diff(actual, expected_lon)
            assert diff <= ARCMINUTE, (
                f"[{label}] cusp {house} {actual:.6f}° vs expected "
                f"{expected_lon:.6f}° -> {diff * 60:.3f}' off"
            )
            checked += 1

    if exp.cusp_sublords:
        for house, sub in exp.cusp_sublords.items():
            actual = chart.cusps[house - 1].sub_lord
            assert actual == sub, (
                f"[{label}] cusp {house} sub-lord {actual} vs expected {sub}"
            )
            checked += 1

    assert checked > 0  # guarded by the skip below


@pytest.mark.parametrize("golden", GOLDEN_CHARTS, ids=lambda g: g.label)
def test_vedic_chart(golden: GoldenChart):
    if not _has_any_expectation(golden.vedic):
        pytest.skip(f"{golden.label}: Vedic expected values are TODO (fill from JHora)")
    chart = compute_chart(golden.birth, *PRESET_VEDIC)
    _check(chart, golden.vedic, f"{golden.label}/vedic")


@pytest.mark.parametrize("golden", GOLDEN_CHARTS, ids=lambda g: g.label)
def test_kp_chart(golden: GoldenChart):
    if not _has_any_expectation(golden.kp):
        pytest.skip(f"{golden.label}: KP expected values are TODO (fill from KP tool)")
    chart = compute_chart(golden.birth, *PRESET_KP)
    _check(chart, golden.kp, f"{golden.label}/kp")


@pytest.mark.parametrize("golden", GOLDEN_CHARTS, ids=lambda g: g.label)
def test_dasha_balance_at_birth(golden: GoldenChart):
    if golden.dasha_balance is None:
        pytest.skip(f"{golden.label}: dasha balance is TODO (fill from JHora)")
    expected_lord, expected_years = golden.dasha_balance
    chart = compute_chart(golden.birth, *PRESET_VEDIC)
    lord, years, _days = balance_at_birth(chart.planets["Moon"].longitude)
    assert lord == expected_lord, (
        f"[{golden.label}] dasha lord {lord} vs expected {expected_lord}"
    )
    assert abs(years - expected_years) <= DASHA_YEAR_TOL, (
        f"[{golden.label}] balance {years:.4f}y vs expected {expected_years:.4f}y"
    )


@pytest.mark.parametrize("golden", GOLDEN_CHARTS, ids=lambda g: g.label)
def test_varga_placements(golden: GoldenChart):
    if not golden.vargas:
        pytest.skip(f"{golden.label}: varga placements are TODO (fill from JHora)")
    chart = compute_chart(golden.birth, *PRESET_VEDIC)
    for code, placements in golden.vargas.items():
        vc = divisional_chart(chart, code)
        for planet, expected_sign in placements.items():
            actual = vc.planet_signs[planet]
            assert actual == expected_sign, (
                f"[{golden.label}] {code} {planet} {actual} vs expected "
                f"{expected_sign}"
            )
