"""Tests for the Phase-7 agent — offline, with a scripted fake LLM.

No Anthropic SDK and no API key are needed: the agent talks to an injected
``LLMClient`` fake that replays a fixed script, while the tools run against the
real deterministic engine. This verifies the loop, tool dispatch, grounding,
and the guardrail wiring without any network.
"""

import json

import pytest

from engine import knowledge
from engine.birth_data import BirthData
from engine.agent import (
    SYSTEM_PROMPT,
    TOOL_NAMES,
    TOOL_SPECS,
    AstrologyAgent,
    ToolKit,
)
from engine.agent.llm import LLMResult


BIRTH = BirthData(1990, 1, 1, 12, 0, 0, 28.6139, 77.2090, "Asia/Kolkata")


def _tool_use(uid, name, inp):
    return {"type": "tool_use", "id": uid, "name": name, "input": inp}


class ScriptedLLM:
    """Replays a fixed list of LLMResults; records what it was sent."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def complete(self, system, messages, tools, max_tokens):
        self.calls.append({"system": system, "messages": [dict(m) for m in messages],
                           "tools": tools})
        return self.script.pop(0)


class AlwaysToolUse:
    """Never stops — used to exercise the max-iterations guard."""

    def complete(self, system, messages, tools, max_tokens):
        return LLMResult("tool_use", [_tool_use("t", "get_yogas", {})])


# --------------------------------------------------------------------------- #
# Tool surface
# --------------------------------------------------------------------------- #
def test_tool_specs_cover_planned_tools():
    for name in ("compute_chart", "get_vimshottari_dasha", "dasha_at",
                 "get_divisional_chart", "get_yogas", "get_kp_significators",
                 "get_cuspal_sublords", "get_ruling_planets", "judge_event_kp",
                 "get_lal_kitab_chart", "get_remedies", "search_texts"):
        assert name in TOOL_NAMES
    # Every spec is a well-formed Anthropic tool definition.
    for t in TOOL_SPECS:
        assert t["input_schema"]["type"] == "object"


def test_system_prompt_has_grounding_guardrail():
    p = SYSTEM_PROMPT.lower()
    assert "never" in p and "tool result" in p
    assert "separately then synthesize" in p


# --------------------------------------------------------------------------- #
# ToolKit dispatch (birth bound server-side)
# --------------------------------------------------------------------------- #
def test_dispatch_grounds_in_engine_output():
    kit = ToolKit(BIRTH)
    out = kit.dispatch("compute_chart", {"system": "vedic"})
    assert out == knowledge.compute_chart_facts(BIRTH, "vedic")
    json.dumps(out)   # serializable for tool_result content


def test_dispatch_event_and_search():
    kit = ToolKit(BIRTH)
    j = kit.dispatch("judge_event_kp", {"event": "marriage"})
    assert j["deciding_cusp"] == 7 and "verdict" in j
    s = kit.dispatch("search_texts", {"query": "marriage cuspal sub lord",
                                      "system": "kp"})
    assert s["passages"] and s["passages"][0]["source"]


def test_dispatch_errors_are_returned_not_raised():
    kit = ToolKit(BIRTH)
    assert "error" in kit.dispatch("no_such_tool", {})
    assert "error" in kit.dispatch("get_divisional_chart", {})        # missing code
    assert "error" in kit.dispatch("get_house_info", {"house": 99})   # bad house


# --------------------------------------------------------------------------- #
# Agent loop
# --------------------------------------------------------------------------- #
def test_agent_runs_tools_then_answers():
    script = [
        LLMResult("tool_use", [
            _tool_use("u1", "compute_chart", {"system": "vedic"}),
            _tool_use("u2", "get_yogas", {}),
        ]),
        LLMResult("tool_use", [
            _tool_use("u3", "search_texts",
                      {"query": "raja yoga", "system": "vedic"}),
        ]),
        LLMResult("end_turn", [
            {"type": "text", "text": "Vedic indicates a Dhana yoga; in synthesis..."},
        ]),
    ]
    llm = ScriptedLLM(script)
    agent = AstrologyAgent(BIRTH, llm=llm)
    result = agent.ask("Will I be wealthy?")

    assert result.answer.startswith("Vedic indicates")
    assert result.iterations == 3 and not result.stopped_early
    assert result.grounded_tools() == ["compute_chart", "get_yogas", "search_texts"]
    # The compute_chart record is the real engine output (grounding).
    assert result.tool_calls[0].output == knowledge.compute_chart_facts(BIRTH, "vedic")


def test_agent_feeds_tool_results_back_as_user_turn():
    script = [
        LLMResult("tool_use", [_tool_use("u1", "get_yogas", {})]),
        LLMResult("end_turn", [{"type": "text", "text": "done"}]),
    ]
    llm = ScriptedLLM(script)
    AstrologyAgent(BIRTH, llm=llm).ask("any yogas?")

    # On the 2nd call the history must contain assistant tool_use + user tool_result.
    second_history = llm.calls[1]["messages"]
    assert second_history[1]["role"] == "assistant"
    assert second_history[2]["role"] == "user"
    tr = second_history[2]["content"][0]
    assert tr["type"] == "tool_result" and tr["tool_use_id"] == "u1"
    json.loads(tr["content"])   # tool result is JSON


def test_agent_respects_max_iterations():
    agent = AstrologyAgent(BIRTH, llm=AlwaysToolUse(), max_iterations=3)
    result = agent.ask("loop forever")
    assert result.stopped_early
    assert result.iterations == 3
    assert len(result.tool_calls) == 3
