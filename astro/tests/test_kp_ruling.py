"""Deterministic tests for KP Ruling Planets."""

from engine.birth_data import BirthData
from engine.kp_ruling import ruling_planets


def test_day_lord_from_weekday():
    # 1990-01-01 was a Monday -> day lord Moon.
    rp = ruling_planets(
        BirthData(1990, 1, 1, 12, 0, 0, 28.6139, 77.2090, "Asia/Kolkata"))
    assert rp.day_lord == "Moon"


def test_day_lord_saturday():
    # 1985-07-13 was a Saturday -> day lord Saturn.
    rp = ruling_planets(
        BirthData(1985, 7, 13, 21, 30, 0, 40.7128, -74.0060, "America/New_York"))
    assert rp.day_lord == "Saturn"


def test_ruling_planets_structure():
    rp = ruling_planets(
        BirthData(1990, 1, 1, 12, 0, 0, 28.6139, 77.2090, "Asia/Kolkata"))
    # Seven lord slots are filled and ordered/deduped without blanks.
    for field in (rp.moon_sign_lord, rp.moon_star_lord, rp.moon_sub_lord,
                  rp.lagna_sign_lord, rp.lagna_star_lord, rp.lagna_sub_lord):
        assert field
    assert rp.ordered
    assert len(rp.ordered) == len(set(rp.ordered))   # deduped
