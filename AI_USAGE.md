# AI Usage Disclosure

Claude Code (Anthropic) is used as a mentor in "code-along" mode (rules in `CLAUDE.md`):
it may scaffold structure, write stubs/boilerplate/process docs, and give partial snippets in chat.
Core logic (Cypher, repository, planning, evidence rules, simulator dynamics, agent tools, API bodies,
UI components, evaluation) is written by Siddharth.

| date | file/function | type | what I (Siddharth) did |
|---|---|---|---|
| 2026-10-15 | Whole repo tree (Step 0.1) | scaffold | Specified structure in CLAUDE.md; reviewed tree. |
| 2026-10-15 | `.gitignore`, `docker-compose.yml`, `.env.example`, `backend/pyproject.toml`, `frontend/{package.json,tsconfig.json,vite.config.ts,index.html,src/main.tsx,src/App.tsx}`, `backend/ripple/config.py` | boilerplate | Chose stack defaults (uv, Py 3.12, Claude, minimal frontend). |
| 2026-10-15 | All `backend/ripple/**.py` stubs, `.cypher` headers, scenario/eval YAML placeholders, `tests/` skips | scaffold (stubs only, `NotImplementedError` bodies) | To implement. |
| 2026-10-15 | `PROGRESS.md`, `docs/decisions.md` | process docs | — |
