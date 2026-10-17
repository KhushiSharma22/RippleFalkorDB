# Decisions (ADR-lite)

## D-001 — Python tooling: uv, Python 3.12
- **Context:** Local Python is 3.14; some wheels lag new releases.
- **Options:** pip+venv; uv; poetry.
- **Decision:** uv, `requires-python >=3.11`, pin 3.12 via `.python-version`.
- **Why:** fast, lockfile, one tool; 3.12 avoids wheel gaps.

## D-002 — LLM provider: Claude (Anthropic SDK)
- **Context:** Agent layer needs tool calling; validators are deterministic and have final say.
- **Decision:** Anthropic SDK, model configured via `LLM_MODEL`.
- **Why:** native tool use; provider only affects `agent/orchestrator.py`.

## D-003 — Cypher lives in `.cypher` files, loaded by name
- **Context:** Submission must show "the queries the product depends on"; judges must find them fast.
- **Options:** inline strings in Python; `.cypher` files + loader.
- **Decision:** one file per query under `graph/queries/<area>/`, header comment
  (purpose, parameters, returns, used-by), loaded via `query_loader.py`, called only from `repository.py`.
- **Why:** single auditable surface; makes the "graph is load-bearing" claim checkable.
