"""Deterministic tests for divisional charts (vargas)."""

import pytest

from engine.constants import SIGN_NAMES, SIGN_SPAN
from engine.varga import VARGAS, varga_sign, varga_sign_index


def _sign(name):
    return SIGN_NAMES.index(name)


def test_d1_is_identity():
    for lon in (0.0, 45.0, 123.456, 359.9):
        assert varga_sign_index(lon, "D1") == int(lon // SIGN_SPAN)


def test_d9_is_continuous_navamsa():
    # Navamsas are 3°20' and cycle continuously through the signs from Aries.
    # Sample mid-part longitudes (avoid exact boundaries where float floor is
    # ambiguous); add a tiny epsilon to the reference for the same reason.
    step = 360.0 / 108.0
    for lon in (1.0, 5.0, 31.0, 65.0, 200.123, 358.0):
        assert varga_sign_index(lon, "D9") == int(lon / step + 1e-9) % 12


def test_d9_known_starts():
    assert varga_sign(1.0, "D9") == "Aries"        # movable sign from itself
    assert varga_sign(31.0, "D9") == "Capricorn"   # Taurus (fixed) from the 9th
    assert varga_sign(61.0, "D9") == "Libra"       # Gemini (dual) from the 5th
    assert varga_sign(91.0, "D9") == "Cancer"      # Cancer (movable) from itself


def test_d2_hora():
    assert varga_sign(5.0, "D2") == "Leo"       # odd sign, first half -> Sun
    assert varga_sign(20.0, "D2") == "Cancer"   # odd sign, second half -> Moon
    assert varga_sign(35.0, "D2") == "Cancer"   # even sign (Taurus), first half
    assert varga_sign(50.0, "D2") == "Leo"      # even sign, second half


def test_d3_drekkana_trines():
    assert varga_sign(5.0, "D3") == "Aries"        # 1st
    assert varga_sign(15.0, "D3") == "Leo"         # 5th
    assert varga_sign(25.0, "D3") == "Sagittarius"  # 9th


def test_d30_trimsamsa_bands():
    # Odd sign (Aries) bands: Mars/Saturn/Jupiter/Mercury/Venus.
    assert varga_sign(3.0, "D30") == "Aries"        # 0-5 Mars
    assert varga_sign(8.0, "D30") == "Aquarius"     # 5-10 Saturn
    assert varga_sign(15.0, "D30") == "Sagittarius"  # 10-18 Jupiter
    assert varga_sign(22.0, "D30") == "Gemini"      # 18-25 Mercury
    assert varga_sign(28.0, "D30") == "Libra"       # 25-30 Venus
    # Even sign (Taurus) bands: Venus/Mercury/Jupiter/Saturn/Mars.
    assert varga_sign(33.0, "D30") == "Taurus"      # 0-5 Venus
    assert varga_sign(40.0, "D30") == "Virgo"       # 5-12 Mercury
    assert varga_sign(58.0, "D30") == "Scorpio"     # 25-30 Mars


@pytest.mark.parametrize("code", list(VARGAS))
def test_every_varga_returns_valid_sign_over_full_sweep(code):
    lon = 0.0
    while lon < 360.0:
        idx = varga_sign_index(lon, code)
        assert 0 <= idx < 12
        lon += 0.37   # irregular step to probe many sub-parts


def test_unknown_varga_raises():
    with pytest.raises(ValueError):
        varga_sign_index(10.0, "D5")
