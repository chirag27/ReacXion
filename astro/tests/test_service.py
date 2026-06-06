"""Tests for the FastAPI backend (engine + agent over HTTP)."""

import pytest
from fastapi.testclient import TestClient

from engine.agent.llm import LLMResult
from service.app import create_app

BIRTH = {"year": 1990, "month": 1, "day": 1, "hour": 12, "minute": 0, "second": 0,
         "latitude": 28.6139, "longitude": 77.2090, "timezone": "Asia/Kolkata",
         "name": "Test"}


class _FakeLLM:
    """One tool call, then a final answer — exercises /ask without a key."""

    def __init__(self):
        self._n = 0

    def complete(self, system, messages, tools, max_tokens):
        self._n += 1
        if self._n == 1:
            return LLMResult("tool_use", [
                {"type": "tool_use", "id": "x", "name": "get_yogas", "input": {}}])
        return LLMResult("end_turn", [{"type": "text", "text": "Grounded reading."}])


@pytest.fixture
def client():
    return TestClient(create_app())


@pytest.fixture
def client_with_agent():
    return TestClient(create_app(agent_llm=_FakeLLM()))


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "marriage" in body["events"] and "D9" in body["vargas"]


def test_chart_endpoint(client):
    r = client.post("/chart", json={**BIRTH, "system": "kp"})
    assert r.status_code == 200
    body = r.json()
    assert body["ayanamsa"] == "kp"
    assert len(body["cusps"]) == 12
    assert set(body["planets"]) >= {"Sun", "Moon", "Ketu"}


def test_kp_judge_and_significators(client):
    j = client.post("/kp/judge", json={**BIRTH, "event": "marriage"}).json()
    assert j["deciding_cusp"] == 7 and "verdict" in j
    s = client.post("/kp/significators", json={**BIRTH, "house": 7}).json()
    assert s["house"] == 7 and isinstance(s["significators"], list)


def test_report_bundle(client):
    r = client.post("/report", json=BIRTH)
    assert r.status_code == 200
    body = r.json()
    for key in ("vedic_chart", "kp_chart", "navamsa", "dasha", "yogas",
                "lal_kitab", "remedies", "time_confidence"):
        assert key in body
    assert body["ashtakavarga"]["total"] == 337


def test_confidence_and_sensitivity(client):
    c = client.post("/confidence", json=BIRTH).json()
    assert c["level"] in ("high", "medium", "low")
    s = client.post("/sensitivity", json={**BIRTH, "minutes": 2}).json()
    assert s["confidence"] in ("high", "low")


def test_invalid_birth_returns_422(client):
    bad = {**BIRTH, "month": 13}
    assert client.post("/chart", json={**bad, "system": "vedic"}).status_code == 422


def test_ask_without_agent_returns_503(client):
    r = client.post("/ask", json={**BIRTH, "question": "career?"})
    assert r.status_code == 503


def test_ask_with_injected_agent(client_with_agent):
    r = client_with_agent.post("/ask", json={**BIRTH, "question": "any yogas?"})
    assert r.status_code == 200
    body = r.json()
    assert body["answer"] == "Grounded reading."
    assert body["tool_calls"][0]["tool"] == "get_yogas"
