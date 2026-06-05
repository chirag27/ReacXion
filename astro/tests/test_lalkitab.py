"""Deterministic tests for the Lal Kitab chart, pakka ghar, and states."""

from tests._fakechart import make_chart
from engine.lalkitab import (
    AWAKENED,
    ASLEEP,
    BLIND,
    PAKKA_GHAR,
    LalKitabChart,
    lal_kitab_house,
)
from engine.constants import GRAHA_NAMES


def test_fixed_grid_house_is_sign():
    assert lal_kitab_house(5.0) == 1       # Aries -> 1
    assert lal_kitab_house(35.0) == 2      # Taurus -> 2
    assert lal_kitab_house(355.0) == 12    # Pisces -> 12


def test_pakka_ghar_table_complete():
    assert set(PAKKA_GHAR) == set(GRAHA_NAMES)
    assert all(1 <= h <= 12 for h in PAKKA_GHAR.values())


def test_in_pakka_ghar_detection():
    # Sun's pakka ghar is the 1st (Aries); place Sun in Aries.
    lk = LalKitabChart.from_chart(make_chart(ascendant=200.0, Sun=5.0,
                                             Moon=100, Mars=130))
    assert lk.states["Sun"].house == 1
    assert lk.states["Sun"].in_pakka_ghar is True
    assert "Sun" in lk.planets_in_pakka_ghar()


def test_state_awakened_with_company():
    # Two grahas in the same khana -> awakened.
    lk = LalKitabChart.from_chart(make_chart(ascendant=0.0, Sun=5.0, Moon=10.0))
    assert lk.states["Sun"].state == AWAKENED
    assert "Moon" in lk.states["Sun"].companions


def test_state_blind_when_alone_and_unaspected():
    # Sun alone in Taurus (house 2); all others clustered in Aries, whose
    # aspects (3/4/5/7/8/9/10) never reach house 2.
    lk = LalKitabChart.from_chart(make_chart(
        ascendant=0.0, Sun=35.0,
        Moon=1, Mars=2, Mercury=3, Jupiter=4, Venus=6, Saturn=7,
        Rahu=8, Ketu=9))
    assert lk.states["Sun"].state == BLIND


def test_state_asleep_when_alone_but_aspected():
    # Sun alone in Taurus (house 2), Mars in Scorpio (house 8) aspects it (8th sees 2nd).
    lk = LalKitabChart.from_chart(make_chart(
        ascendant=0.0, Sun=35.0, Mars=220.0,
        Moon=1, Mercury=3, Jupiter=4, Venus=6, Saturn=125, Rahu=130, Ketu=135))
    st = lk.states["Sun"]
    assert st.companions == []
    assert "Mars" in st.aspected_by
    assert st.state == ASLEEP


def test_ascendant_house_is_its_sign():
    lk = LalKitabChart.from_chart(make_chart(ascendant=190.0))  # Libra
    assert lk.ascendant_house == 7
    assert lk.house_sign_name(7) == "Libra"
