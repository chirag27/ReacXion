"""Structural smoke tests for chart computation.

Ephemeris-dependent but assertion targets are structural invariants (counts,
relationships, ranges) rather than transcribed reference values — those live in
``test_golden.py``.
"""

import pytest

from engine.constants import GRAHA_NAMES, SIGN_NAMES
from engine.birth_data import BirthData
from engine.chart import compute_kp_chart, compute_vedic_chart


@pytest.fixture
def sample_birth():
    return BirthData(1990, 1, 1, 12, 0, 0, 28.6139, 77.2090, "Asia/Kolkata",
                     name="sample")


def test_all_nine_grahas_present(sample_birth):
    chart = compute_vedic_chart(sample_birth)
    assert set(chart.planets) == set(GRAHA_NAMES)
    assert len(chart.planets) == 9


def test_ketu_opposite_rahu(sample_birth):
    chart = compute_vedic_chart(sample_birth)
    rahu = chart.planets["Rahu"].longitude
    ketu = chart.planets["Ketu"].longitude
    assert ketu == pytest.approx((rahu + 180.0) % 360.0, abs=1e-9)


def test_longitudes_in_range(sample_birth):
    chart = compute_vedic_chart(sample_birth)
    for p in chart.planets.values():
        assert 0.0 <= p.longitude < 360.0
        assert p.sign in SIGN_NAMES
        assert 1 <= p.pada <= 4


def test_twelve_cusps_and_ascendant(sample_birth):
    chart = compute_vedic_chart(sample_birth)
    assert len(chart.cusps) == 12
    assert [c.house for c in chart.cusps] == list(range(1, 13))
    assert 0.0 <= chart.ascendant < 360.0


def test_whole_sign_cusps_snap_to_sign_start(sample_birth):
    chart = compute_vedic_chart(sample_birth)
    for c in chart.cusps:
        assert c.longitude % 30.0 == pytest.approx(0.0, abs=1e-6)


def test_placidus_house1_equals_ascendant(sample_birth):
    chart = compute_kp_chart(sample_birth)
    assert chart.cusps[0].longitude == pytest.approx(chart.ascendant, abs=1e-6)


def test_kp_vs_vedic_ayanamsa_differ(sample_birth):
    vedic = compute_vedic_chart(sample_birth)
    kp = compute_kp_chart(sample_birth)
    # KP and Lahiri ayanamsa differ by a few arcminutes -> Sun longitude shifts.
    assert vedic.planets["Sun"].longitude != kp.planets["Sun"].longitude


def test_every_planet_and_cusp_has_kp_sublord(sample_birth):
    chart = compute_kp_chart(sample_birth)
    for p in chart.planets.values():
        assert p.sub_lord and p.nakshatra_lord and p.sign_lord
    for c in chart.cusps:
        assert c.sub_lord and c.nakshatra_lord and c.sign_lord
