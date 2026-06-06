"""Provider-neutral LLM interface for the agent loop.

The agent maintains conversation history in Anthropic's content-block format
(text / tool_use / tool_result), so the real client and the test fake share the
exact wire shape. ``complete()`` returns a normalised :class:`LLMResult`
regardless of provider, keeping the agent loop free of SDK specifics and fully
testable offline (no API key, no network) via a scripted fake.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Protocol


@dataclass
class LLMResult:
    stop_reason: str
    blocks: List[Dict] = field(default_factory=list)  # Anthropic content blocks

    def text(self) -> str:
        return "".join(b.get("text", "") for b in self.blocks if b["type"] == "text")

    def tool_uses(self) -> List[Dict]:
        return [b for b in self.blocks if b["type"] == "tool_use"]


class LLMClient(Protocol):
    def complete(
        self,
        system: str,
        messages: List[Dict],
        tools: List[Dict],
        max_tokens: int,
    ) -> LLMResult:
        ...


class AnthropicLLM:
    """Default client — Claude via the official Anthropic SDK (lazy-imported).

    Uses the manual tool-use loop pattern (the agent drives the loop). Adaptive
    thinking is on by default; thinking blocks are preserved verbatim across
    turns so signatures round-trip correctly.
    """

    def __init__(
        self,
        model: str = "claude-opus-4-8",
        api_key: str = None,
        thinking: bool = True,
    ):
        self.model = model
        self.thinking = thinking
        self._api_key = api_key
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            import anthropic  # lazy — only needed for live calls
            self._client = (anthropic.Anthropic(api_key=self._api_key)
                            if self._api_key else anthropic.Anthropic())
        return self._client

    def complete(self, system, messages, tools, max_tokens) -> LLMResult:
        client = self._ensure_client()
        kwargs = dict(model=self.model, max_tokens=max_tokens, system=system,
                      tools=tools, messages=messages)
        if self.thinking:
            kwargs["thinking"] = {"type": "adaptive"}
        resp = client.messages.create(**kwargs)
        return LLMResult(resp.stop_reason, [_block_to_dict(b) for b in resp.content])


def _block_to_dict(block) -> Dict:
    """Normalise an SDK content block to a plain dict re-sendable as history."""
    t = block.type
    if t == "text":
        return {"type": "text", "text": block.text}
    if t == "tool_use":
        return {"type": "tool_use", "id": block.id, "name": block.name,
                "input": block.input}
    if t == "thinking":
        return {"type": "thinking", "thinking": block.thinking,
                "signature": block.signature}
    if t == "redacted_thinking":
        return {"type": "redacted_thinking", "data": block.data}
    # Unknown block types pass through via model_dump if available.
    return block.model_dump() if hasattr(block, "model_dump") else {"type": t}
