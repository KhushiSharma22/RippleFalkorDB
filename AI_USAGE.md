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
| 2026-10-17 | `graph/client.py` (`get_db`, `get_graph`), `tests/conftest.py` (`db`, `graph` fixtures), `tests/integration/test_roundtrip.py` | fuller snippet (`unblock me`, line-by-line) | Designed: shared client, test-graph naming/isolation, fail-loud on unreachable DB. Typed code from chat; integration test passes (fail-first run not confirmed). |
| 2026-10-17 | `backend/scripts/cyberwave_proof.py` | fuller snippet (full throwaway proof script; SDK live-view snapshot gotcha found in SDK source) | Typed + ran; measuring credit cost. |
| 2026-10-17 | `backend/scripts/list_assets.py`; proof-script edits (UUID lookup, nudge, twin reuse) | snippet (debugging, SDK source read by AI) | Typed + ran; observed robot in browser. |
| 2026-10-17 | `backend/scripts/list_twins.py` | snippet (diagnostic) | Typed + ran; compared twin IDs with browser. |
| 2026-10-17 | `backend/scripts/cyberwave_reposition_proof.py`; `affect("sim")` edits | fuller snippet (proof script; SDK source traced by AI) | Typed + ran; proof passed; supplied environment id; tested keyboard teleop in browser. |
| 2026-10-17 | `robot/base.py` (Pose, RobotAdapter, arrived), `robot/mock_adapter.py`, `tests/unit/test_robot_adapter.py` | AI-written (`write it: step 0.3`) | Designed/approved interface (command vs. verified arrival, coords from graph, teleport mock with failure injection); reviewing. |
| 2026-10-17 | `docs/graph-model.md` v1, `docs/graph-model-preview.cypher`, `backend/scripts/load_model_preview.py` | AI-written (on request; scoped down: Siddharth decides DP1–DP5) | Validating in FalkorDB Browser; answering decision points. |
| 2026-10-17 | `docs/judge-prep.md` (Q&A study sheet, Milestone 0) | AI-written (process doc, on request) | Studying; to rehearse answers in own words. |
| 2026-10-17 | `simulator/scenarios/healthy_8.yaml` | AI-written (scenario data transcribed from proposal numbers + graph-model v1) | Chose seeding design (D-010, D-011); writing seed code. |
| 2026-10-17 | `graph/query_loader.py`, `graph/schema.py`, `graph/seed.py`, `tests/integration/test_seed.py`, seed template headers | AI-written (on request; pushed back once: Siddharth writes the 2 Cypher clauses in `queries/seed/*.cypher`) | Chose design (D-010, D-011); types the Cypher; runs tests. |
| 2026-10-17 | Milestone 1: `ripple/scenario.py`, scenarios (`healthy_8` additions, `standby_down`, `healthy_5`), `evidence/models.py`, `evidence/freshness.py`, `graph/repository.py`, `graph/seed.py` (observations), `simulator/*`, `planning/validator.py` (`check_action`, `compare`), `agent/orchestrator.py`, `tests/test_architecture.py`, `tests/scenarios/test_vertical_slice.py`, `tests/unit/test_evidence_and_simulator.py`; 12 `.cypher` headers | AI-written (`write it: Milestone 1`; pushed back once: Siddharth pastes the 12 query bodies) | Requested scope; pastes/reads each query; runs tests. |
| 2026-10-17 | 12 Milestone 1 Cypher query bodies | snippet (given in chat, typed/pasted by Siddharth) | Pasted + read each; ran tests. |
| 2026-10-17 | 9 M2–M4 Cypher queries (impact ×3, stale_evidence, hypotheses ×2, route via algo.SPpaths, create_decision, decision_trace) + headers | snippet (given in chat, tested by AI against seeded graph incl. edge cases) | Pasting + reading; wiring into repository in M2–M4. |
