"""Deterministic tests for planetary dignity."""

from engine.dignity import natural_relationship, planet_dignity


def test_exaltation():
    assert planet_dignity("Sun", 5.0).state == "exalted"        # Aries
    assert planet_dignity("Moon", 35.0).state == "exalted"      # Taurus
    assert planet_dignity("Saturn", 195.0).state == "exalted"   # Libra
    assert planet_dignity("Sun", 5.0).is_exalted is True


def test_debilitation():
    assert planet_dignity("Sun", 185.0).state == "debilitated"   # Libra
    assert planet_dignity("Saturn", 5.0).state == "debilitated"  # Aries
    assert planet_dignity("Jupiter", 280.0).state == "debilitated"  # Capricorn
    assert planet_dignity("Saturn", 5.0).is_debilitated is True


def test_moolatrikona_vs_own():
    # Sun: Leo 0-20 is moolatrikona, 20-30 is own.
    assert planet_dignity("Sun", 130.0).state == "moolatrikona"  # Leo 10°
    assert planet_dignity("Sun", 145.0).state == "own"           # Leo 25°
    # Mars: Aries 0-12 moolatrikona; Scorpio is plain own.
    assert planet_dignity("Mars", 5.0).state == "moolatrikona"   # Aries 5°
    assert planet_dignity("Mars", 215.0).state == "own"          # Scorpio 5°


def test_friend_and_enemy_signs():
    # Sun in Cancer (lord Moon, a friend of Sun).
    assert planet_dignity("Sun", 100.0).state == "friend"
    # Sun in Taurus (lord Venus, an enemy of Sun).
    assert planet_dignity("Sun", 40.0).state == "enemy"
    # Sun in Virgo (lord Mercury, neutral to Sun).
    assert planet_dignity("Sun", 160.0).state == "neutral"


def test_dispositor_recorded():
    d = planet_dignity("Mars", 100.0)   # Cancer -> lord Moon
    assert d.sign == "Cancer"
    assert d.sign_lord == "Moon"


def test_natural_relationship_table():
    assert natural_relationship("Sun", "Moon") == "friend"
    assert natural_relationship("Sun", "Saturn") == "enemy"
    assert natural_relationship("Sun", "Mercury") == "neutral"


def test_nodes_are_neutral_without_exaltation():
    d = planet_dignity("Rahu", 45.0)
    assert d.state == "neutral"
    assert d.is_exalted is False and d.is_debilitated is False
