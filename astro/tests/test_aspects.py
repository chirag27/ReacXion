"""Deterministic tests for graha drishti (Parashari aspects)."""

from types import SimpleNamespace

from engine.aspects import aspected_houses, aspects_between, graha_drishti


def _chart(**planet_longitudes):
    """Build a minimal duck-typed chart for the aspect functions."""
    planets = {
        name: SimpleNamespace(longitude=lon)
        for name, lon in planet_longitudes.items()
    }
    return SimpleNamespace(planets=planets)


def test_aspected_houses_specials():
    assert aspected_houses("Mars") == [4, 7, 8]
    assert aspected_houses("Jupiter") == [5, 7, 9]
    assert aspected_houses("Saturn") == [3, 7, 10]
    assert aspected_houses("Sun") == [7]      # default


def test_seventh_aspect_is_opposite_sign():
    # Sun at 5° Aries (sign 0) aspects sign 6 (Libra).
    chart = _chart(Sun=5.0, Moon=185.0)   # Moon at 5° Libra
    asp = graha_drishti(chart)
    assert 6 in asp["Sun"].aspected_sign_indices
    assert "Moon" in asp["Sun"].aspected_planets


def test_mars_special_aspects_4_7_8():
    # Mars at 10° Aries (sign 0) -> aspects signs 3 (4th), 6 (7th), 7 (8th).
    chart = _chart(Mars=10.0, Mercury=100.0, Venus=190.0, Saturn=215.0)
    asp = graha_drishti(chart)["Mars"]
    assert set(asp.aspected_sign_indices) == {3, 6, 7}
    # Mercury(Cancer,3), Venus(Libra,6), Saturn(Scorpio,7) are all aspected.
    assert asp.aspected_planets == ["Mercury", "Saturn", "Venus"]


def test_jupiter_aspects_5_and_9():
    # Jupiter at 0° Aries aspects signs 4 (5th) and 8 (9th) plus 6 (7th).
    chart = _chart(Jupiter=0.0)
    asp = graha_drishti(chart)["Jupiter"]
    assert set(asp.aspected_sign_indices) == {4, 6, 8}


def test_aspects_between_helper():
    chart = _chart(Saturn=0.0, Sun=60.0)   # Saturn sign0; 3rd aspect -> sign2 (Gemini)
    # Sun at 60° = 0° Gemini (sign 2) -> aspected by Saturn's 3rd aspect.
    assert aspects_between(chart, "Saturn", "Sun") is True
    assert aspects_between(chart, "Sun", "Saturn") is False
