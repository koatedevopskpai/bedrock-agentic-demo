"""Tests — agent loop, tool dispatch and trace correctness (all mocked, no AWS)."""
from __future__ import annotations

from src.agent import ReActAgent
from src.bedrock import BedrockClient
from src.tools import get_tool


def _agent() -> ReActAgent:
    return ReActAgent(BedrockClient(mode="mock"))


def test_calculator_tool_dispatch() -> None:
    result = _agent().run("What is 15 times 27?")
    assert "405" in result.answer or any(
        s.get("tool") == "calculator" for s in result.trace
    )


def test_datetime_tool_dispatch() -> None:
    result = _agent().run("What is the current date?")
    assert any(s.get("tool") == "datetime" for s in result.trace)


def test_trace_is_auditable() -> None:
    result = _agent().run("What is 15 times 27?")
    assert len(result.trace) >= 2  # decision + observation
    # every observation must come from a real tool
    for step in result.trace:
        if step.get("step") == "observe":
            get_tool(step["tool"])  # raises if unknown


def test_tool_registry_functions() -> None:
    assert "405" in get_tool("calculator").fn(expr="15 * 27")
    assert "error" in get_tool("calculator").fn(expr="__import__('os')")
