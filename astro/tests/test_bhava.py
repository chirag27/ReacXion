"""Tests for the bhava signification / karaka reference data."""

from engine.bhava import BHAVA, houses_signifying, karakas, significations


def test_all_twelve_bhavas_present():
    assert set(BHAVA) == set(range(1, 13))
    for h, b in BHAVA.items():
        assert b.number == h
        assert b.name
        assert b.karakas
        assert b.significations


def test_known_karakas():
    assert karakas(1)[0] == "Sun"        # tanu karaka
    assert karakas(7)[0] == "Venus"      # spouse
    assert karakas(10)[0] == "Mercury"   # karma (primary)
    assert "Jupiter" in karakas(5)       # children


def test_significations_lookup():
    assert "career" in significations(10)
    assert "spouse" in significations(7)


def test_houses_signifying_keyword():
    assert 7 in houses_signifying("marriage")
    assert 10 in houses_signifying("career")
    # 4th and 9th both relate to a parent.
    assert houses_signifying("mother") == [4]
