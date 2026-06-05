"""Deterministic tests for the Vimshottari dasha engine."""

from datetime import datetime, timedelta, timezone

import pytest

from engine.constants import NAK_SPAN, VIMSHOTTARI_ORDER, VIMSHOTTARI_YEARS
from engine.dasha import (
    balance_at_birth,
    dasha_at,
    vimshottari_dasha,
)

BIRTH = datetime(1990, 1, 1, 6, 30, tzinfo=timezone.utc)


def test_balance_full_at_nakshatra_start():
    # 0° = start of Ashwini (Ketu); the whole 7-year period remains.
    lord, years, days = balance_at_birth(0.0)
    assert lord == "Ketu"
    assert years == pytest.approx(7.0)


def test_balance_half_at_nakshatra_midpoint():
    lord, years, _ = balance_at_birth(NAK_SPAN / 2)
    assert lord == "Ketu"
    assert years == pytest.approx(3.5)


def test_balance_rolls_to_next_lord():
    # Start of Bharani (Venus, 20 years).
    lord, years, _ = balance_at_birth(NAK_SPAN)
    assert lord == "Venus"
    assert years == pytest.approx(20.0)


def test_first_mahadasha_lord_matches_moon_nakshatra():
    mahas = vimshottari_dasha(NAK_SPAN / 2, BIRTH, depth=1)
    # dasha_at(birth) should land inside the starting Ketu mahadasha.
    chain = dasha_at(mahas, BIRTH)
    assert chain[0].lord == "Ketu"


def test_mahadasha_sequence_follows_vimshottari_order():
    mahas = vimshottari_dasha(0.0, BIRTH, depth=1)
    lords = [m.lord for m in mahas[:9]]
    assert lords == VIMSHOTTARI_ORDER  # starts at Ketu, full cycle


def test_periods_are_contiguous_at_every_level():
    mahas = vimshottari_dasha(123.45, BIRTH, depth=4)
    for a, b in zip(mahas, mahas[1:]):
        assert a.end == b.start
    for maha in mahas[:3]:
        for a, b in zip(maha.children, maha.children[1:]):
            assert a.end == b.start
        for antar in maha.children[:3]:
            for a, b in zip(antar.children, antar.children[1:]):
                assert a.end == b.start


def test_children_durations_sum_to_parent():
    mahas = vimshottari_dasha(200.0, BIRTH, depth=2)
    for maha in mahas[:5]:
        child_span = sum(c.duration_days for c in maha.children)
        assert child_span == pytest.approx(maha.duration_days, rel=1e-9)


def test_antardasha_starts_with_mahadasha_lord():
    mahas = vimshottari_dasha(0.0, BIRTH, depth=2)
    for maha in mahas[:9]:
        assert maha.children[0].lord == maha.lord


def test_dasha_at_returns_full_depth_chain():
    mahas = vimshottari_dasha(77.0, BIRTH, depth=4)
    chain = dasha_at(mahas, BIRTH + timedelta(days=5000))
    assert [p.level for p in chain] == [1, 2, 3, 4]
    # The chain is properly nested in time.
    for parent, child in zip(chain, chain[1:]):
        assert parent.start <= child.start
        assert child.end <= parent.end


def test_dasha_at_requires_aware_datetime():
    mahas = vimshottari_dasha(0.0, BIRTH, depth=1)
    with pytest.raises(ValueError):
        dasha_at(mahas, datetime(1995, 1, 1))


def test_total_first_cycle_is_120_years():
    mahas = vimshottari_dasha(0.0, BIRTH, depth=1, year_length_days=365.25)
    first_nine = mahas[:9]
    span_days = (first_nine[-1].end - first_nine[0].start).total_seconds() / 86400
    assert span_days == pytest.approx(120 * 365.25, rel=1e-9)
