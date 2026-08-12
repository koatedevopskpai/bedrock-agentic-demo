"""tools.py — a small tool registry behind one interface (dependency inversion)."""

from __future__ import annotations

import datetime
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class Tool:
    name: str
    description: str
    fn: Callable[..., str]


def _calculator(expr: str) -> str:
    try:
        # safe eval: only arithmetic allowed via allowed AST node types
        import ast
        import operator

        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
        }

        def _eval(node: ast.AST) -> float:
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in ops:
                return ops[type(node.op)](_eval(node.left), _eval(node.right))
            if isinstance(node, ast.UnaryOp) and type(node.op) in ops:
                return ops[type(node.op)](_eval(node.operand))
            raise ValueError(f"unsupported expression: {expr}")

        return str(_eval(ast.parse(expr, mode="eval").body))
    except Exception as exc:  # noqa: BLE001
        return f"error: {exc}"


def _datetime() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _search(query: str) -> str:
    # Stub for a real search tool — returns deterministic fixtures in demo.
    fixtures = {
        "ai agents": "AI agents are LLM-driven systems that take actions using tools.",
        "bedrock": "Amazon Bedrock is a managed service for foundation models.",
        "rag": "RAG grounds LLM answers in retrieved documents to reduce hallucination.",
    }
    for key, val in fixtures.items():
        if key in query.lower():
            return val
    return "No fixture for query; a live implementation would call a search API."


TOOL_REGISTRY: list[Tool] = [
    Tool("calculator", "Evaluate a numeric expression (e.g. '15 * 27').", _calculator),
    Tool("datetime", "Return the current UTC date and time.", _datetime),
    Tool("search", "Search the knowledge base for a topic.", _search),
]


def get_tool(name: str) -> Tool:
    for t in TOOL_REGISTRY:
        if t.name == name:
            return t
    raise KeyError(f"unknown tool: {name}")
