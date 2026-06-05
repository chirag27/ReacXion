"""Deterministic tests for Lal Kitab rina (debt) detection."""

from tests._fakechart import make_chart
from engine.lalkitab import LalKitabChart
from engine.lalkitab_debts import detect_rinas, rina_report


def _names(lk):
    return {r.sanskrit for r in detect_rinas(lk)}


# A clean chart: no malefic in houses 1/4/5/6/7/9 and no afflicter conjoining
# Sun/Moon/Venus/Mercury -> no rinas. Rahu(h2)/Ketu(h8) are the only node split
# that keeps both nodes out of every rina house.
CLEAN = dict(
    ascendant=65.0,
    Sun=65, Moon=66, Mercury=67, Venus=68, Jupiter=69,   # all in Gemini (h3)
    Mars=290, Saturn=291,                                 # Capricorn (h10)
    Rahu=45, Ketu=225,                                    # Taurus(h2)/Scorpio(h8)
)


def test_clean_chart_has_no_rinas():
    lk = LalKitabChart.from_chart(make_chart(**CLEAN))
    assert detect_rinas(lk) == []


def test_pitra_rin_from_malefic_in_ninth():
    chart = dict(CLEAN, Saturn=250)   # Saturn -> Sagittarius (house 9)
    lk = LalKitabChart.from_chart(make_chart(**chart))
    assert "Pitra Rin" in _names(lk)


def test_matri_rin_from_malefic_in_fourth():
    chart = dict(CLEAN, Ketu=100, Rahu=280)   # Ketu -> Cancer (house 4)
    lk = LalKitabChart.from_chart(make_chart(**chart))
    assert "Matri Rin" in _names(lk)


def test_stri_rin_from_afflicted_venus():
    # Venus conjoined with Rahu -> Stri Rin (place the pair in a non-rina house).
    chart = dict(CLEAN, Venus=40, Rahu=41, Ketu=221)   # Taurus (house 2)
    lk = LalKitabChart.from_chart(make_chart(**chart))
    assert "Stri Rin" in _names(lk)


def test_rina_report_lists_all_with_status():
    lk = LalKitabChart.from_chart(make_chart(**CLEAN))
    report = rina_report(lk)
    assert len(report) == 6
    assert all(r.present is False for r in report)
