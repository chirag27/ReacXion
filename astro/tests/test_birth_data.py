"""Deterministic tests for the BirthData timezone -> UTC conversion.

These do not depend on the ephemeris and assert exact, known UTC instants —
the conversion is the #1 chart bug, so it is pinned tightly.
"""

from datetime import datetime, timezone

import pytest

from engine.birth_data import BirthData, TimezoneError


def test_india_fixed_no_dst():
    b = BirthData(1990, 1, 1, 12, 0, 0, 28.6139, 77.2090, "Asia/Kolkata")
    # IST is UTC+5:30 with no DST -> 06:30 UTC.
    assert b.to_utc() == datetime(1990, 1, 1, 6, 30, tzinfo=timezone.utc)
    assert b.utc_offset_hours() == pytest.approx(5.5)


def test_numeric_offset_matches_iana():
    iana = BirthData(1990, 1, 1, 12, 0, 0, 28.6139, 77.2090, "Asia/Kolkata")
    fixed = BirthData(1990, 1, 1, 12, 0, 0, 28.6139, 77.2090, 5.5)
    assert iana.to_utc() == fixed.to_utc()


def test_us_daylight_saving_offset():
    # 1985-07-13 is EDT (UTC-4), so 21:30 local -> 01:30 UTC next day.
    b = BirthData(1985, 7, 13, 21, 30, 0, 40.7128, -74.0060, "America/New_York")
    assert b.to_utc() == datetime(1985, 7, 14, 1, 30, tzinfo=timezone.utc)
    assert b.utc_offset_hours() == pytest.approx(-4.0)


def test_us_standard_time_offset():
    # January is EST (UTC-5).
    b = BirthData(1985, 1, 13, 21, 30, 0, 40.7128, -74.0060, "America/New_York")
    assert b.to_utc() == datetime(1985, 1, 14, 2, 30, tzinfo=timezone.utc)
    assert b.utc_offset_hours() == pytest.approx(-5.0)


def test_seconds_precision_preserved():
    b = BirthData(2000, 6, 15, 4, 5, 37, 0.0, 0.0, 0.0)
    assert b.to_utc() == datetime(2000, 6, 15, 4, 5, 37, tzinfo=timezone.utc)


def test_nonexistent_springforward_time_rejected():
    # US spring-forward 2021-03-14: 02:00-03:00 local does not exist.
    with pytest.raises(TimezoneError):
        BirthData(2021, 3, 14, 2, 30, 0, 40.7128, -74.0060,
                  "America/New_York").to_utc()


def test_ambiguous_fallback_fold_distinguishes_instants():
    # US fall-back 2021-11-07: 01:30 local occurs twice (EDT then EST).
    early = BirthData(2021, 11, 7, 1, 30, 0, 40.7128, -74.0060,
                      "America/New_York", fold=0).to_utc()
    late = BirthData(2021, 11, 7, 1, 30, 0, 40.7128, -74.0060,
                     "America/New_York", fold=1).to_utc()
    # The two readings are exactly one hour apart.
    assert (late - early).total_seconds() == 3600


def test_invalid_coordinates_rejected():
    with pytest.raises(ValueError):
        BirthData(2000, 1, 1, 0, 0, 0, 95.0, 0.0, 0.0)
    with pytest.raises(ValueError):
        BirthData(2000, 1, 1, 0, 0, 0, 0.0, 200.0, 0.0)


def test_invalid_datetime_rejected():
    with pytest.raises(ValueError):
        BirthData(2000, 2, 30, 0, 0, 0, 0.0, 0.0, 0.0)
