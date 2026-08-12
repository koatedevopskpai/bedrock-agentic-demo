"""app.py — FastAPI service exposing the agent via POST /ask."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .agent import ReActAgent
from .bedrock import BedrockClient

app = FastAPI(title="Bedrock Agentic Demo", version="0.1.0")


class AskRequest(BaseModel):
    query: str
    mode: str = "mock"  # 'mock' | 'bedrock'


class AskResponse(BaseModel):
    answer: str
    trace: list[dict]


@app.post("/ask")
def ask(req: AskRequest) -> AskResponse:
    agent = ReActAgent(BedrockClient(mode=req.mode))
    result = agent.run(req.query)
    return AskResponse(answer=result.answer, trace=result.trace)


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}
