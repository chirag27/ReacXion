"""Interpretation-quality eval harness for the agent.

Calculation correctness is regression-tested by the golden charts; this catches
regressions in the *interpretation* layer. Each case asserts that a question
gets **grounded** — the agent must call at least one of the tools relevant to
the topic before answering. The harness runs against any ``LLMClient`` (the real
Claude client for a live eval, or a scripted fake offline), so it doubles as a
deterministic CI check on the loop and as a live quality gate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Tuple

from .agent import AgentResult, AstrologyAgent


@dataclass
class EvalCase:
    question: str
    expect_tools_any: Tuple[str, ...]   # at least one of these must be called
    topic: str = ""


# A small, extensible interpretation eval set covering the main consultation
# topics. Each case names the tools a grounded answer must touch.
DEFAULT_EVAL_SET: List[EvalCase] = [
    EvalCase("Will I have a successful career?",
             ("compute_chart", "get_yogas", "judge_event_kp",
              "get_kp_significators"), topic="career"),
    EvalCase("When am I likely to get married?",
             ("judge_event_kp", "get_cuspal_sublords", "get_vimshottari_dasha",
              "dasha_at"), topic="marriage"),
    EvalCase("What does my chart say about wealth and gains?",
             ("get_yogas", "compute_chart", "get_ashtakavarga",
              "judge_event_kp"), topic="wealth"),
    EvalCase("Are there any ancestral debts and remedies for me?",
             ("get_rinas", "get_remedies", "get_lal_kitab_chart"),
             topic="lalkitab"),
    EvalCase("Which dasha am I running now and what does it bring?",
             ("get_vimshottari_dasha", "dasha_at"), topic="timing"),
]


@dataclass
class EvalOutcome:
    case: EvalCase
    answer: str
    tools_called: List[str]
    grounded: bool                 # called >= 1 tool at all
    on_topic: bool                 # called >= 1 of the expected tools
    passed: bool


@dataclass
class EvalReport:
    outcomes: List[EvalOutcome] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(o.passed for o in self.outcomes)

    @property
    def total(self) -> int:
        return len(self.outcomes)

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.outcomes else 0.0


def evaluate(
    agent_factory: Callable[[], AstrologyAgent],
    cases: List[EvalCase] = None,
) -> EvalReport:
    """Run each case on a fresh agent and score grounding + topical relevance."""
    cases = cases or DEFAULT_EVAL_SET
    report = EvalReport()
    for case in cases:
        agent = agent_factory()
        result: AgentResult = agent.ask(case.question)
        tools = result.grounded_tools()
        grounded = len(tools) > 0
        on_topic = any(t in case.expect_tools_any for t in tools)
        report.outcomes.append(EvalOutcome(
            case=case, answer=result.answer, tools_called=tools,
            grounded=grounded, on_topic=on_topic,
            passed=grounded and on_topic))
    return report
