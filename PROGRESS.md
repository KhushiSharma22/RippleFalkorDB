# Progress

## Current step
**0.1 — Scaffold + FalkorDB round-trip.** Scaffold done; round-trip pending.

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
