# bedrock-agentic-demo — an agentic AI demo on AWS Bedrock

An agentic AI demo that runs on **AWS Bedrock** (Claude) with a **FastAPI** service, a **tool-calling** loop, **Terraform** IaC, and **CI**. Built to demonstrate the AWS track of my portfolio: Bedrock as code, agent design, and a quality gate — without pretending it's a full enterprise platform (that's `agentic-platform-aws`).

## What it demonstrates

- **AWS Bedrock** — invokes Claude via the Bedrock runtime (`boto3`); IAM-guarded model access
- **Agentic loop** — ReAct-style tool calling: the model decides, tools execute, observation returns
- **Tools** — a small registry (`search`, `calculator`, `datetime`) behind one interface (swap-in, testable)
- **FastAPI service** — `POST /ask` returns the agent's answer + the tool trace (auditability)
- **Terraform** — provisions a least-privilege role for Bedrock model access (apply-safe, module-scoped)
- **CI** — tests run in **mock mode** (no AWS creds, zero cost); real Bedrock runs when creds are present

## Quick start

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 1. Run the agent in mock mode (no AWS) — proves the loop + tools
python src/cli.py --mode mock --query "What is 15 times 27?"

# 2. Run the FastAPI service
uvicorn src.app:app --reload --port 8080
# POST /ask  {"query": "What is the current date?", "mode": "mock"}

# 3. Real Bedrock (needs AWS creds + region with Claude enabled)
#    export AWS_PROFILE=...  (or AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY)
python src/cli.py --mode bedrock --query "Summarise the last 3 search results for AI agents"
```

## The agent loop (ReAct-style, mocked for CI)

```
user query ─► model decides next action ─► dispatch tool ─► observation ─► loop ─► answer + trace
```

Every step is recorded in `trace[]` and returned — the same auditability I ship in production agents.

## Terraform

`terraform/` creates an IAM role granting the **minimum** Bedrock `InvokeModel` permission for the demo (no broad admin). Example:

```bash
cd terraform
terraform init && terraform plan   # review, then apply
```

> Guardrail: the role is scoped to the demo region + model IDs. This is the least-privilege pattern I apply to every agent.

## CI

`.github/workflows/ci.yml` — lint + unit tests in mock mode on every push/PR (free, no AWS). A real-Bedrock smoke test runs only when `AWS_ACCESS_KEY_ID` is present as a secret.

## Project layout

```
src/
  app.py          FastAPI service (POST /ask)
  agent.py        ReAct agent loop + trace
  tools.py        tool registry (search/calculator/datetime)
  bedrock.py      Bedrock runtime client (boto3) with mock fallback
  cli.py          CLI runner (mock|bedrock)
tests/
  test_agent.py   loop, tool dispatch, trace correctness (mocked)
  test_tools.py   tool behaviour
terraform/
  main.tf         least-privilege Bedrock role
  variables.tf
.github/workflows/ci.yml
```

## Related portfolio

- `agentic-platform-aws` — the full multi-agent + eval platform design on AWS
- `llm-evals-demo` — the RAGAS quality bar / CI gate

Built by George Kpai (github.com/koate-kpai).
