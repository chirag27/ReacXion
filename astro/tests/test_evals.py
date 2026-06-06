"""Tests for the interpretation-quality eval harness (offline, scripted LLM)."""

from engine.birth_data import BirthData
from engine.agent import AstrologyAgent
from engine.agent.llm import LLMResult
from engine.agent.evals import DEFAULT_EVAL_SET, EvalCase, evaluate

BIRTH = BirthData(1990, 1, 1, 12, 0, 0, 28.6139, 77.2090, "Asia/Kolkata")


def _scripted(tool_name):
    """A fake LLM that calls one named tool then answers — always on-topic."""
    class S:
        def __init__(self):
            self.n = 0

        def complete(self, system, messages, tools, max_tokens):
            self.n += 1
            if self.n == 1:
                return LLMResult("tool_use", [
                    {"type": "tool_use", "id": "i", "name": tool_name, "input": {}}])
            return LLMResult("end_turn", [{"type": "text", "text": "answer"}])
    return S()


def test_default_eval_set_is_nonempty_and_typed():
    assert DEFAULT_EVAL_SET
    assert all(isinstance(c, EvalCase) and c.expect_tools_any
               for c in DEFAULT_EVAL_SET)


def test_evaluate_passes_when_agent_calls_expected_tool():
    # Build an agent whose fake LLM calls the first expected tool of each case.
    cases = DEFAULT_EVAL_SET

    def factory_for(case):
        return lambda: AstrologyAgent(BIRTH, llm=_scripted(case.expect_tools_any[0]))

    from engine.agent.evals import evaluate as ev
    for case in cases:
        report = ev(factory_for(case), [case])
        o = report.outcomes[0]
        assert o.grounded and o.on_topic and o.passed


def test_evaluate_fails_when_no_tools_called():
    class NoTool:
        def complete(self, system, messages, tools, max_tokens):
            return LLMResult("end_turn", [{"type": "text", "text": "ungrounded"}])

    report = evaluate(lambda: AstrologyAgent(BIRTH, llm=NoTool()),
                      [DEFAULT_EVAL_SET[0]])
    assert report.pass_rate == 0.0
    assert not report.outcomes[0].grounded
