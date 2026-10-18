# Ripple

An evidence-driven inspection robot that prevents cascading equipment failures.
FalkorDB + Cyberwave hackathon project. Concept: [docs/proposal.md](docs/proposal.md).

> All facility data, capacities and failure modes are **synthetic simulation assumptions**.

## Setup
TODO(siddharth): fill in once Step 0.1 round-trip works.

```bash
cp .env.example .env
docker compose up -d falkordb      # Redis protocol :6379, browser UI :3000
cd backend && uv sync && uv run pytest
```

## Graph data model
See [docs/graph-model.md](docs/graph-model.md). TODO(siddharth): summary + diagram.

## Queries the product depends on
Index: [docs/queries.md](docs/queries.md). Source: `backend/ripple/graph/queries/**.cypher`.

## Architecture
See [docs/architecture.md](docs/architecture.md).

## Tracks entered
TODO(siddharth)

## AI assistance disclosure
Built with Claude Code (Anthropic) as a coding assistant; design decisions are recorded in [docs/decisions.md](docs/decisions.md).
