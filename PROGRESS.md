# Progress

## Current step
**Milestone 1 — vertical slice** (Milestone 0 complete).

## Log

### 2026-10-15 — Session 1
- **Done:** Stack confirmed (uv / Python 3.12, FastAPI, Pydantic v2, pytest, FalkorDB in Docker,
  Claude for agent layer, React+TS+Vite with graph-viz lib TBD). Repo scaffolded per CLAUDE.md §4:
  stubs, boilerplate, process docs only.
- **Tested:** nothing yet.
- **Open issues:**
  - Verify FalkorDB image tag/ports and `GRAPH.COPY` availability against current docs.
  - Verify FalkorDB shortest-path support (needed for `robot/route_to_inspection_point`).
  - Cyberwave SDK package name/capabilities unknown until 0.2.
  - Graph-viz library choice deferred to Milestone 5.
- **Next:** `docker compose up`, implement `graph/client.py`, round-trip one node from Python.

### 2026-10-17 — Session 2
- **Done (0.1):** Docker Desktop + FalkorDB up; uv installed, `uv sync` OK. `graph/client.py`
  (`get_db` cached shared client, `get_graph`), conftest fixtures (session ping that fails loudly;
  per-test `test_<name>_<hex>` graph with tolerant teardown), `test_asset_round_trip`.
- **Tested:** `uv run pytest -m integration` → 1 passed; no leftover graphs.
- **Open:** explain-back answers for 0.1 owed; fail-first run not confirmed.
- **Next:** 0.2 Cyberwave proof.
- **0.2 in progress:** SDK read (v0.7.3); decisions D-004 (credit budget), D-005 (open-loop + verify, coords in graph). Proof script pending run.
- **0.2 result:** blocked: playground accepts commands but robot doesn't move and no pose returns (D-006).
  Scripts: `backend/scripts/cyberwave_proof.py`, `list_assets.py`. Action: ask Cyberwave team.
- **0.2 DONE:** reposition proof passes (D-007): before (0,0) → after (1.5,-0.5) via independent REST readback.
  Locomotion unresolved (D-006) — question for Cyberwave team.
- **0.3 DONE (AI-written on request):** `robot/base.py` (`Pose`, `RobotAdapter` Protocol, `arrived`),
  `robot/mock_adapter.py` (teleport + `fail_next_moves`), `tests/unit/test_robot_adapter.py` (5 tests).
- **Tested:** `uv run pytest` → 6 passed, 2 skipped (architecture stubs); ruff clean.
- **Open:** `CyberwaveRobotAdapter` (edit_position per D-007) not yet written; explain-back for 0.1/0.2 owed.
- **0.4 drafted:** `docs/graph-model.md` v1 + `docs/graph-model-preview.cypher` + `scripts/load_model_preview.py`
  (27 nodes / 51 rels in `model_preview`; impact + robot-location queries return expected rows).
- **0.4 DONE:** DP1–DP5 accepted (D-008).
- **Next:** Milestone 1 vertical slice.
