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

## D-004 — Cyberwave budget: proof + demo only (revised: see end)
- **Context:** 50 API credits total; per-call cost not documented publicly. `affect("sim"/"mujoco")` starts billable MuJoCo runs.
- **Decision:** Dev, tests and the full evaluation run on `MockRobotAdapter`. Cyberwave used for the 0.2 proof and the final demo only, in `affect("playground")`. Measure credits per proof run; reserve ~half for demo recording.
- **Why:** eval (3 configs × 6 scenarios) on Cyberwave could exhaust the budget; mock keeps dev unblocked.

## D-005 — Robot movement: open-loop burst + single pose verification; coordinates in graph
- **Context:** SDK exposes velocity bursts (`move_forward`, `turn_*`) and `pose.get()`; no navigate-to-waypoint (`missions.py` is explicitly aspirational).
- **Options:** closed-loop correction (many calls), open-loop dead reckoning, `edit_position` teleport (editor layout, not locomotion).
- **Decision:** per hop, issue the burst, then one `pose.get()` to verify arrival within tolerance. Location `x, y` stored on `Location` nodes in FalkorDB; adapter receives target coordinates, holds no topology.
- **Why:** credit-cheap, honest ("commanded, then verified" — predicted ≠ observed), keeps the graph load-bearing (invariant #1).

## D-006 — Cyberwave proof result (0.2): blocked in playground; proceed on mock
- **Finding (2026-10-17):** SDK v0.7.3 authenticates, lists catalog, creates a Go2 twin in the Quickstart
  Environment, connects MQTT (mqtt.cyberwave.com:8883). But in `affect("playground")`:
  `pose.get()` returns no pose (view `.pose is None`), and `locomotion.move_forward` does not move the
  twin (observed in browser), even when reusing an existing twin whose controller policy is attached.
- **Narrowed down:** the browser environment defaults to LIVE (expects paired hardware). In SIMULATE,
  keyboard teleop (W) moves the same twin (`03a3e4d0…`, the only twin in the workspace), but SDK
  commands do not. Traced in SDK source: `affect("playground")` → runtime `simulation` → commands
  published on `cyberwave/twin/{uuid}/command` with `source_type="sim_tele"`. Hypothesis: browser
  playground simulates keyboard input locally and does not consume SDK MQTT commands. Unconfirmed;
  question for Cyberwave team.
- **Gotchas found:** `cw.twin("unitree/go2")` raised "not found" because `get_by_registry_id` swallows
  all exceptions (worked via asset UUID); `cw.twin(asset)` creates a NEW twin per call (reuse via `twin_id=`);
  `pose.get()` returns a live view (snapshot with `translation_dict()`).
- **Decision:** proceed with `MockRobotAdapter` (0.3). Ask Cyberwave team how to get locomotion + pose
  in playground; revisit the Cyberwave adapter if unblocked. Not claiming Cyberwave integration until proven.
- **Why:** CLAUDE.md 0.2 fallback; protect remaining credits; honest scope.

- **Update (MuJoCo):** `affect("sim", environment_id=..., duration=60)` starts MuJoCo at ~0.01 credits/min
  (~0.60/h) — credits are not the constraint (revises D-004's premise). MuJoCo started and reported
  running, but Go2 velocity commands still produced no pose (likely needs a locomotion controller; unconfirmed).

## D-007 — Cyberwave adapter moves the twin via `edit_position` (repositioning, not locomotion)
- **Context:** Locomotion + pose readback unresolved in playground and MuJoCo (D-006).
- **Proof (2026-10-17):** `twin.edit_position(x=1.5, y=-0.5)` then independent REST readback
  `cw.twins.get_raw(uuid).position_x/y` → (0,0) → (1.5,-0.5). Script: `backend/scripts/cyberwave_reposition_proof.py`.
- **Decision:** `CyberwaveRobotAdapter.move_to` = `edit_position` to the target Location's (x, y) from the graph;
  `current_pose` = REST readback. Described honestly as "twin repositioning", not walking.
  Dev/tests/eval on `MockRobotAdapter`; Cyberwave adapter for demo visualization.
- **Why:** deterministic, no MQTT/sim dependency, no sim credits; same `RobotAdapter` interface, so
  swapping in real locomotion later changes only `move_to`.

## D-008 — Graph model v1 (`docs/graph-model.md`): DP1–DP5 accepted by Siddharth
- DP1 state only as Observations · DP2 FEEDS + CONNECTED_TO both · DP3 InspectionPoint own label ·
  DP4 `(:Robot)-[:AT]->(:Location)` moved on verified arrival · DP5 branches write `source:"predicted"` Observations.
- **Status:** drafted by Claude; Siddharth reviewed and agreed with all five on 2026-10-17. Rationale per DP is in the graph-model.md table.

## D-009 — Run dev scripts as modules (`uv run python -m scripts.<name>`)
- **Context:** `.venv` lives under iCloud-synced `~/Documents`; macOS flags `_editable_impl_ripple.pth` as hidden and
  Python skips hidden `.pth` files, so `python scripts/x.py` can't import `ripple`.
- **Decision:** invoke scripts with `-m` from `backend/` (adds cwd to `sys.path`). Alternative: move repo out of iCloud.

## D-010 — Seeding Cypher: two template files + label/type whitelist
- **Context:** FalkorDB can't parameterise labels or relationship types (`SET n:$(x)` is a syntax error, verified).
- **Options:** one `.cypher` per label/type (~20 files); inline f-strings in seed.py; two templates with whitelist.
- **Decision (Siddharth):** `queries/seed/create_nodes.cypher` + `create_relationships.cypher` with `{labels}`/`{type}`
  placeholders, filled only from a whitelist derived from graph-model.md; values always passed as `$rows`.
- **Why:** Cypher stays auditable in files (D-003); whitelist prevents injection; batching via UNWIND.

## D-011 — Seed clears via graph delete, then ensure_schema
- **Decision (Siddharth):** `graph.delete()` (tolerating "empty key"), then idempotent `ensure_schema`, then nodes, then relationships.
- **Why:** truly clean slate; FalkorDB errors on re-creating an existing index ("already indexed", verified), so ensure_schema must tolerate it anyway.
- **Scenario files:** one YAML per scenario with `graph:` (known, seeded) and `truth:` (hidden, simulator only).
