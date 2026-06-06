"""The astrology agent — a hand-rolled tool-calling loop.

Deliberately a plain loop (no framework): the agent sends the question to the
LLM with the engine tools, executes any tool calls against the deterministic
:class:`ToolKit`, feeds results back, and repeats until the model produces a
final answer. Every tool call is recorded for traceability, so a reading can be
audited back to the exact engine outputs that grounded it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..birth_data import BirthData
from ..rag import TextStore
from .llm import AnthropicLLM, LLMClient
from .prompt import SYSTEM_PROMPT
from .tools import TOOL_SPECS, ToolKit


@dataclass
class ToolCallRecord:
    tool: str
    input: Dict
    output: Dict


@dataclass
class AgentResult:
    answer: str
    tool_calls: List[ToolCallRecord] = field(default_factory=list)
    iterations: int = 0
    stopped_early: bool = False

    def grounded_tools(self) -> List[str]:
        return [tc.tool for tc in self.tool_calls]


class AstrologyAgent:
    """Tool-calling Jyotish agent over the deterministic engine."""

    def __init__(
        self,
        birth: BirthData,
        llm: Optional[LLMClient] = None,
        store: Optional[TextStore] = None,
        model: str = "claude-opus-4-8",
        max_tokens: int = 8000,
        max_iterations: int = 12,
    ):
        self.birth = birth
        self.toolkit = ToolKit(birth, store)
        self.llm = llm or AnthropicLLM(model=model)
        self.max_tokens = max_tokens
        self.max_iterations = max_iterations

    def ask(self, question: str) -> AgentResult:
        messages: List[Dict] = [{"role": "user", "content": question}]
        records: List[ToolCallRecord] = []
        result = None

        for i in range(1, self.max_iterations + 1):
            result = self.llm.complete(
                system=SYSTEM_PROMPT, messages=messages,
                tools=TOOL_SPECS, max_tokens=self.max_tokens)

            if result.stop_reason != "tool_use":
                return AgentResult(answer=result.text(), tool_calls=records,
                                   iterations=i, stopped_early=False)

            # Echo the assistant turn (incl. any thinking blocks) verbatim.
            messages.append({"role": "assistant", "content": result.blocks})

            tool_results = []
            for tu in result.tool_uses():
                output = self.toolkit.dispatch(tu["name"], tu.get("input", {}))
                records.append(ToolCallRecord(tu["name"], tu.get("input", {}), output))
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu["id"],
                    "content": json.dumps(output, default=str),
                })
            messages.append({"role": "user", "content": tool_results})

        return AgentResult(
            answer=(result.text() if result else "")
            or "(stopped: reached the maximum number of tool iterations)",
            tool_calls=records, iterations=self.max_iterations, stopped_early=True)
