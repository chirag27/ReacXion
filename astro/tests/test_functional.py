"""Deterministic tests for functional (lagna-based) benefic/malefic nature."""

from engine.functional import (
    BENEFIC,
    MALEFIC,
    YOGAKARAKA,
    classify_all,
    functional_nature,
    yogakarakas_for,
)


def test_classic_yogakarakas():
    # The textbook yogakarakas:
    assert functional_nature("Saturn", 1).nature == YOGAKARAKA   # Taurus lagna
    assert functional_nature("Saturn", 6).nature == YOGAKARAKA   # Libra lagna
    assert functional_nature("Mars", 3).nature == YOGAKARAKA     # Cancer lagna
    assert functional_nature("Mars", 4).nature == YOGAKARAKA     # Leo lagna
    assert functional_nature("Venus", 9).nature == YOGAKARAKA    # Capricorn lagna
    assert functional_nature("Venus", 10).nature == YOGAKARAKA   # Aquarius lagna


def test_yogakarakas_for_helper():
    assert "Saturn" in yogakarakas_for(1)   # Taurus
    assert "Mars" in yogakarakas_for(3)     # Cancer


def test_lagna_lord_is_benefic():
    # Aries lagna: Mars rules the 1st (and 8th) -> benefic (lagna lord prevails).
    assert functional_nature("Mars", 0).nature == BENEFIC


def test_dusthana_only_lord_is_malefic():
    # Aries lagna: Mercury rules 3 (Gemini) and 6 (Virgo) -> malefic.
    fn = functional_nature("Mercury", 0)
    assert fn.nature == MALEFIC
    assert sorted(fn.owned_houses) == [3, 6]


def test_nodes_have_no_rulership():
    fn = functional_nature("Rahu", 5)
    assert fn.owned_houses == []
    assert "node" in fn.reason.lower()


def test_classify_all_covers_nine_grahas():
    res = classify_all(0)
    assert len(res) == 9
    assert all(fn.reason for fn in res.values())
