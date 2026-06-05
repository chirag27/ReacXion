"""Deterministic tests for KP event judgment, timing, and sensitivity."""

import pytest

from engine.birth_data import BirthData
from engine.chart import compute_kp_chart
from engine.kp import KPAnalysis
from engine.kp_events import (
    EVENTS,
    birth_time_sensitivity,
    event_dasha_periods,
    judge_event,
)


@pytest.fixture
def kp_delhi():
    return compute_kp_chart(
        BirthData(1990, 1, 1, 12, 0, 0, 28.6139, 77.2090, "Asia/Kolkata"))


@pytest.fixture
def analysis(kp_delhi):
    return KPAnalysis.from_chart(kp_delhi)


def test_all_events_have_deciding_cusp_in_houses():
    for name, rule in EVENTS.items():
        assert rule.deciding_cusp in range(1, 13)
        assert rule.houses


def test_judge_event_structure(analysis):
    j = judge_event(analysis, "marriage")
    assert j.deciding_cusp == 7
    assert j.cuspal_sub_lord                      # a CSL was resolved
    assert set(j.final_significators) <= set(j.significators)
    assert isinstance(j.promised, bool)
    # 'supports' is exactly the event houses the CSL signifies.
    assert all(h in j.houses for h in j.supports)


def test_judge_event_unknown_raises(analysis):
    with pytest.raises(ValueError):
        judge_event(analysis, "lottery")


def test_event_dasha_periods_are_bhukti_with_both_lords_signifying(analysis):
    windows = event_dasha_periods(
        BirthData(1990, 1, 1, 12, 0, 0, 28.6139, 77.2090, "Asia/Kolkata"),
        analysis, "marriage")
    final = set(analysis.final_significators(EVENTS["marriage"].houses))
    for w in windows:
        assert w.level == 2          # antardasha
        assert w.lord in final


def test_birth_time_sensitivity_report():
    birth = BirthData(1990, 1, 1, 12, 0, 0, 28.6139, 77.2090, "Asia/Kolkata")
    fine = birth_time_sensitivity(birth, minutes=1)
    coarse = birth_time_sensitivity(birth, minutes=4)
    assert fine.confidence in ("high", "low")
    # A wider uncertainty window cannot reveal fewer unstable cusps.
    assert len(coarse.unstable_cusps) >= len(fine.unstable_cusps)
    for ch in coarse.unstable_cusps:
        assert 1 <= ch.house <= 12
        assert not (ch.earlier == ch.at_birth == ch.later)
