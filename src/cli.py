"""cli.py — run the agent from the terminal (mock or bedrock)."""

from __future__ import annotations

import argparse

from .agent import ReActAgent
from .bedrock import BedrockClient


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the Bedrock agentic demo.")
    ap.add_argument("--mode", choices=["mock", "bedrock"], default="mock")
    ap.add_argument("--query", default="What is 15 times 27?")
    args = ap.parse_args()

    agent = ReActAgent(BedrockClient(mode=args.mode))
    result = agent.run(args.query)
    print(f"query : {args.query}")
    print(f"answer: {result.answer}")
    print("trace :")
    for step in result.trace:
        print("  ", step)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
