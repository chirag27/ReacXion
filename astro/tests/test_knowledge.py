"""Tests for the Phase-6 codified-rules query API (engine.knowledge)."""

import json

import pytest

from engine import knowledge
from engine.birth_data import BirthData


@pytest.fixture
def birth():
    return BirthData(1990, 1, 1, 12, 0, 0, 28.6139, 77.2090, "Asia/Kolkata")


def test_chart_facts_are_json_serializable(birth):
    facts = knowledge.compute_chart_facts(birth, "kp")
    json.dumps(facts)                      # must not raise
    assert facts["ayanamsa"] == "kp"
    assert set(facts["planets"]) >= {"Sun", "Moon", "Rahu", "Ketu"}
    assert len(facts["cusps"]) == 12


def test_get_yogas_serializable(birth):
    yogas = knowledge.get_yogas(birth)
    json.dumps(yogas)
    assert all({"name", "category", "planets", "triggers"} <= set(y) for y in yogas)


def test_functional_and_dignities(birth):
    fn = knowledge.get_functional_nature(birth)
    assert fn["Jupiter"]["nature"] in ("benefic", "malefic", "yogakaraka", "neutral")
    dig = knowledge.get_dignities(birth)
    assert dig["Mars"]["state"]


def test_ashtakavarga_total_337(birth):
    av = knowledge.get_ashtakavarga(birth)
    assert av["total"] == 337
    assert set(av["sarva_by_house"]) == set(range(1, 13))


def test_house_info(birth):
    info = knowledge.house_info(7)
    assert info["karakas"] == ["Venus"]
    assert "marriage" in info["significations"]


def test_kp_event_judgment_serializable(birth):
    j = knowledge.judge_event_kp(birth, "marriage")
    json.dumps(j)
    assert j["deciding_cusp"] == 7
    assert isinstance(j["promised"], bool)
    assert set(j["final_significators"]) <= set(j["significators"])


def test_dasha_serializable_nested(birth):
    dasha = knowledge.get_vimshottari_dasha(birth, depth=2)
    json.dumps(dasha)
    assert dasha[0]["level"] == 1
    assert dasha[0]["children"][0]["level"] == 2


def test_lalkitab_and_remedies(birth):
    lk = knowledge.get_lal_kitab_chart(birth)
    json.dumps(lk)
    assert set(lk["house_planets"]) == set(range(1, 13))
    rems = knowledge.get_remedies(birth)
    assert all({"target", "kind", "text"} <= set(r) for r in rems)
