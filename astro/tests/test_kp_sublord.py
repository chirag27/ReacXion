"""Structural and known-value tests for the KP sub-lord system.

These are deterministic (no ephemeris) and validate the subdivision arithmetic
itself. Specific sub-lord values can additionally be cross-checked against a
dedicated KP tool once you transcribe them into the golden charts.
"""

import pytest

from engine.constants import NAK_SPAN, VIMSHOTTARI_ORDER, VIMSHOTTARI_YEARS
from engine.kp_sublord import (
    SUB_WIDTH,
    build_kp_249_table,
    resolve,
)


def test_table_has_249_segments():
    table = build_kp_249_table()
    assert len(table) == 249


def test_table_is_contiguous_and_covers_zodiac():
    table = build_kp_249_table()
    assert table[0].start == 0.0
    assert table[-1].end == pytest.approx(360.0)
    for a, b in zip(table, table[1:]):
        assert a.end == pytest.approx(b.start)
        assert a.start < a.end


def test_sub_widths_sum_to_one_nakshatra():
    assert sum(SUB_WIDTH.values()) == pytest.approx(NAK_SPAN)


def test_start_of_zodiac_is_ashwini_ketu_ketu():
    # 0° Aries: sign lord Mars, star lord Ketu (Ashwini), first sub is Ketu.
    lords = resolve(0.0)
    assert lords.sign_lord == "Mars"
    assert lords.star_lord == "Ketu"
    assert lords.sub_lord == "Ketu"


def test_first_sub_boundary_in_ashwini():
    # Ketu's sub in Ashwini spans 7/120 * 13°20' = 0°46'40" = 0.77778°.
    ketu_width = VIMSHOTTARI_YEARS["Ketu"] / 120 * NAK_SPAN
    assert ketu_width == pytest.approx(0.7777778, abs=1e-6)
    # Just inside Ketu sub -> Ketu; just past -> Venus (next in Vimshottari).
    assert resolve(ketu_width - 0.001).sub_lord == "Ketu"
    assert resolve(ketu_width + 0.001).sub_lord == "Venus"


def test_star_lord_cycle_matches_vimshottari_order():
    # The nakshatra (star) lord of nakshatra n is VIMSHOTTARI_ORDER[n % 9].
    for n in range(27):
        mid = n * NAK_SPAN + NAK_SPAN / 2
        assert resolve(mid).star_lord == VIMSHOTTARI_ORDER[n % 9]


def test_resolve_wraps_360():
    assert resolve(360.0).sub_lord == resolve(0.0).sub_lord
    assert resolve(-0.001).star_lord == resolve(359.999).star_lord
