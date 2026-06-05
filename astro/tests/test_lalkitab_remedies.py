"""Deterministic tests for the Lal Kitab remedies engine."""

from tests._fakechart import make_chart
from engine.constants import GRAHA_NAMES
from engine.lalkitab import LalKitabChart
from engine.lalkitab_debts import detect_rinas
from engine.lalkitab_remedies import (
    PLANET_REMEDIES,
    RINA_REMEDIES,
    remedies_for,
)


def test_remedy_tables_cover_all_grahas_and_rinas():
    assert set(PLANET_REMEDIES) == set(GRAHA_NAMES)
    for key in ("Pitra Rin", "Matri Rin", "Stri Rin", "Bahin-Beti Rin",
                "Santan Rin", "Atma Rin"):
        assert key in RINA_REMEDIES


def test_rina_remedy_emitted_for_detected_rina():
    # Saturn in the 9th -> Pitra Rin -> its remedy.
    lk = LalKitabChart.from_chart(make_chart(
        ascendant=65.0, Saturn=250,
        Sun=65, Moon=66, Mercury=67, Venus=68, Jupiter=69,
        Mars=290, Rahu=45, Ketu=225))
    rinas = detect_rinas(lk)
    rems = remedies_for(lk, rinas)
    pitra = [r for r in rems if r.target == "Pitra Rin"]
    assert pitra and pitra[0].kind == "rina"
    assert "ancestor" in pitra[0].text.lower()


def test_planet_remedy_for_afflicted_planet():
    # Sun conjoined with Saturn (an afflicter) -> Sun gets a remedy.
    lk = LalKitabChart.from_chart(make_chart(
        ascendant=0.0, Sun=40, Saturn=41,
        Moon=66, Mercury=67, Venus=68, Jupiter=69, Mars=290,
        Rahu=130, Ketu=310))
    rems = remedies_for(lk)
    sun = [r for r in rems if r.target == "Sun" and r.kind == "planet"]
    assert sun
    assert sun[0].text == PLANET_REMEDIES["Sun"]
