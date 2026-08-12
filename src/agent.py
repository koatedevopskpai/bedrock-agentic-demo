"""agent.py — a ReAct-style agent loop that records a full trace."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from .bedrock import BedrockClient
from .tools import TOOL_REGISTRY, get_tool

MAX_STEPS = 6


@dataclass
class AgentResult:
    answer: str
    trace: list[dict] = field(default_factory=list)


class ReActAgent:
    """Reason -> Act -> Observe loop with an audit trace.

    In mock mode the model "decides" deterministically so tests/CI are stable;
    in bedrock mode the model receives the tool catalogue and returns a JSON
    decision, executed by the registry. The trace makes every step auditable.
    """

    def __init__(self, model: BedrockClient, max_steps: int = MAX_STEPS) -> None:
        self.model = model
        self.max_steps = max_steps

    def _tool_catalogue(self) -> str:
        return "\n".join(f"- {t.name}: {t.description}" for t in TOOL_REGISTRY)

    def _decide(self, query: str, history: list[str]) -> dict:
        if self.model.mode == "mock":
            return self._mock_decision(query, history)
        prompt = (
            "You are an agent. Tools:\n"
            f"{self._tool_catalogue()}\n"
            "Return ONLY a JSON object with keys: action ('tool' or 'answer'), "
            f"tool (name if tool), args (dict), thought. History: {'; '.join(history)}\nQuery: {query}"
        )
        raw = self.model.invoke(prompt).text
        return json.loads(raw)

    def _mock_decision(self, query: str, history: list[str]) -> dict:
        lower = query.lower()
        # After one tool observation, terminate with an answer that uses it.
        if history:
            last = history[-1]
            return {"thought": "have observation", "action": "answer", "args": {}, "answer": f"Based on the tool result: {last}"}
        if ("15" in query and "27" in query) or "multiply" in lower or "times" in lower:
            return {"thought": "compute", "action": "tool", "tool": "calculator", "args": {"expr": "15 * 27"}}
        if "date" in lower or "time" in lower:
            return {"thought": "get clock", "action": "tool", "tool": "datetime", "args": {}}
        if "search" in lower or "explain" in lower:
            return {"thought": "look up", "action": "tool", "tool": "search", "args": {"query": query}}
        return {"thought": "direct answer", "action": "answer", "args": {}, "answer": "Mock agent ready."}

    def run(self, query: str) -> AgentResult:
        history: list[str] = []
        trace: list[dict] = []
        for _ in range(self.max_steps):
            decision = self._decide(query, history)
            trace.append(decision)
            if decision.get("action") == "answer":
                answer = decision.get("answer", "I don't have enough context to answer.")
                return AgentResult(answer=answer, trace=trace)
            tool = get_tool(decision.get("tool", ""))
            args = decision.get("args", {})
            observation = tool.fn(**args)
            history.append(f"{tool.name}={observation}")
            trace.append({"step": "observe", "tool": tool.name, "observation": observation})
        return AgentResult(answer="Max steps reached without an answer.", trace=trace)
