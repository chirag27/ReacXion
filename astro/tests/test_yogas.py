"""Deterministic yoga-detection tests on constructed charts with known yogas."""

from tests._fakechart import make_chart
from engine.yogas import detect_yogas


def names(chart):
    return {y.name for y in detect_yogas(chart)}


def yoga_named(chart, name):
    return [y for y in detect_yogas(chart) if y.name == name]


def test_hamsa_pancha_mahapurusha():
    # Jupiter exalted in Cancer (95°) in the 1st house (Cancer ascendant).
    chart = make_chart(ascendant=100.0, Jupiter=95.0,
                       Sun=160, Moon=200, Mars=230, Mercury=20, Venus=260, Saturn=130)
    assert "Hamsa Yoga" in names(chart)
    y = yoga_named(chart, "Hamsa Yoga")[0]
    assert y.planets == ("Jupiter",)
    assert "exalted" in y.description


def test_sasa_pancha_mahapurusha():
    # Saturn in own sign Capricorn (280°) in a kendra (10th from Aries lagna).
    chart = make_chart(ascendant=5.0, Saturn=280.0,
                       Sun=40, Moon=70, Mars=200, Mercury=100, Jupiter=160, Venus=130)
    assert "Sasa Yoga" in names(chart)


def test_gaja_kesari():
    # Jupiter in a kendra (4th) from the Moon.
    chart = make_chart(ascendant=200.0, Moon=10.0, Jupiter=100.0,
                       Sun=250, Mars=280, Mercury=40, Venus=70, Saturn=310)
    assert "Gaja Kesari Yoga" in names(chart)


def test_budha_aditya():
    chart = make_chart(ascendant=0.0, Sun=50.0, Mercury=55.0,
                       Moon=200, Mars=230, Jupiter=160, Venus=300, Saturn=130)
    assert "Budha-Aditya Yoga" in names(chart)


def test_chandra_mangala():
    chart = make_chart(ascendant=0.0, Moon=50.0, Mars=55.0,
                       Sun=200, Mercury=160, Jupiter=300, Venus=130, Saturn=250)
    assert "Chandra-Mangala Yoga" in names(chart)


def test_neecha_bhanga_raja_yoga():
    # Sun debilitated in Libra (190°); dispositor Venus in a kendra from lagna.
    chart = make_chart(ascendant=190.0, Sun=190.0, Venus=100.0,
                       Moon=20, Mars=230, Mercury=300, Jupiter=160, Saturn=70)
    matches = yoga_named(chart, "Neecha Bhanga Raja Yoga")
    assert matches and matches[0].planets == ("Sun",)
    assert matches[0].cancellation   # a cancellation reason was recorded


def test_kemadruma_present_when_moon_isolated():
    # Moon in Aries; no company in Aries/Taurus/Pisces.
    chart = make_chart(ascendant=10.0, Moon=10.0,
                       Mars=100, Mercury=130, Jupiter=160, Venus=190, Saturn=220,
                       Sun=40)
    assert "Kemadruma Yoga" in names(chart)


def test_kemadruma_cancelled_by_neighbour():
    # Venus in Taurus = 2nd from the Moon -> not Kemadruma.
    chart = make_chart(ascendant=10.0, Moon=10.0,
                       Mars=100, Mercury=130, Jupiter=160, Venus=40.0, Saturn=220,
                       Sun=70)
    assert "Kemadruma Yoga" not in names(chart)


def test_kendra_trikona_raja_yoga_by_conjunction():
    # Aries lagna: Mars (1st lord, kendra) conjunct Jupiter (9th lord, trikona).
    chart = make_chart(ascendant=5.0, Mars=200.0, Jupiter=205.0,
                       Sun=40, Moon=70, Mercury=100, Venus=130, Saturn=310)
    raja = yoga_named(chart, "Raja Yoga")
    assert any(set(y.planets) == {"Mars", "Jupiter"} for y in raja)
