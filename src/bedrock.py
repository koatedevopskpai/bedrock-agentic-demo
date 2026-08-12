"""bedrock.py — AWS Bedrock runtime client with a mock fallback for CI/offline."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


@dataclass
class ModelResponse:
    text: str
    usage: dict = field(default_factory=dict)


class BedrockClient:
    """Thin wrapper over boto3 Bedrock Runtime.

    mode="mock" returns a deterministic echo so tests and CI run with zero AWS
    cost. mode="bedrock" invokes Claude (anthropic.claude-3-5-sonnet) via
    boto3 and requires valid AWS credentials + model enabled in the region.
    """

    MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

    def __init__(self, mode: str = "mock", region: str | None = None) -> None:
        self.mode = mode
        self.region = region or os.getenv("AWS_REGION", "eu-west-1")
        self._client = None
        if mode == "bedrock":
            import boto3

            self._client = boto3.client("bedrock-runtime", region_name=self.region)

    def invoke(self, prompt: str) -> ModelResponse:
        if self.mode == "mock":
            return self._mock_invoke(prompt)
        return self._bedrock_invoke(prompt)

    def _mock_invoke(self, prompt: str) -> ModelResponse:
        # Deterministic: mimic the agent's JSON tool-decision contract for CI.
        snippet = prompt[:40]
        text = '{"thought": "mock mode", "action": "answer", "observation": "' + snippet + '"}'
        return ModelResponse(text=text, usage={"input_tokens": 0, "output_tokens": 0})

    def _bedrock_invoke(self, prompt: str) -> ModelResponse:
        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "temperature": 0.2,
                "messages": [{"role": "user", "content": prompt}],
            }
        )
        resp = self._client.invoke_model(
            modelId=self.MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=body,
        )
        payload = json.loads(resp["body"].read())
        usage = payload.get("usage", {})
        return ModelResponse(
            text=payload.get("content", [{}])[0].get("text", ""),
            usage={"input_tokens": usage.get("input_tokens", 0), "output_tokens": usage.get("output_tokens", 0)},
        )
