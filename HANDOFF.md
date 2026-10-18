# Ripple: handoff

Status as of 17 Oct 2026. For anyone picking up the project.

## What we're building

**Ripple** is an inspection robot that prevents cascading equipment failures. We're entering it in the **FalkorDB + Cyberwave hackathon**.

Picture a cooling facility: a primary supply, a standby supply, two valves, a shared header, critical **Machine A** (needs 4 units) and lower-priority **Machine B** (needs 3). When the primary supply fails, the obvious fix can disrupt other machines. Ripple handles this in five steps:

1. Traces dependencies in a graph.
2. Works out which facts it doesn't know yet, for example whether the standby is healthy.
3. Sends a robot to inspect those facts.
4. Picks an intervention that keeps critical service running.
5. Checks by observation that the intervention worked.

All equipment and numbers are synthetic simulation assumptions. The full concept is in [docs/proposal.md](docs/proposal.md).

## Why it's built this way

Hackathon rules: FalkorDB must be the primary database and do real work. If you remove it, the product must break. So:

- **The graph is load-bearing.** Topology, prerequisites, evidence, robot locations and inspection points all come from Cypher queries in `backend/ripple/graph/queries/`. There's no in-memory copy.
- **Hidden truth stays hidden.** The simulator knows the real state, and Ripple only learns it through location-gated robot observations. An AST test enforces this.
- **Predicted ≠ observed.** Command sent → ack → verified by a new observation. An ack never counts as success.

We're protecting four differentiators: **multi-hop impact analysis, evidence freshness, decision-driven inspection, and hypothetical branches via `GRAPH.COPY`.**

## Where things are

| Path | What |
|---|---|
| `backend/ripple/graph/` | FalkorDB client, seeding, repository (the only place Cypher runs), `queries/*.cypher` |
| `backend/ripple/simulator/` | Hidden truth, facility flow model, controls, location-gated sensors, `scenarios/*.yaml` |
| `backend/ripple/agent/orchestrator.py` | Core loop: trace impact → choose plan (decision-driven inspection) → execute → verify service |
| `backend/ripple/planning/` | `validator.py` (prerequisites + freshness), `capacity.py` (supply vs demand), `inspection_ranker.py` (decision relevance score), `transition_model.py` (predicted effects) |
| `backend/ripple/evidence/` | Observation model, freshness windows, beliefs (latest fresh evidence), hypothesis rules |
| `backend/ripple/robot/` | `RobotAdapter` Protocol, `MockRobotAdapter` |
| `docs/graph-model.md` | Node labels, relationships, the 5 key modelling decisions |
| `docs/decisions.md` | Every non-obvious decision (D-001 … D-014). **Read this first.** |
| `docs/queries.md` | Index of every Cypher query and its caller |
| `docs/judge-prep.md` | Likely judge questions with answers |
| `PROGRESS.md` | Running log |

## Run it

```bash
docker compose up -d falkordb                 # FalkorDB on :6379, Browser UI on :3000
cd backend && uv sync                         # needs uv (brew install uv); Python 3.12
uv run pytest -v                              # expect 35 passed
uv run python -m scripts.load_model_preview   # toy graph "model_preview" to view in the Browser
```

Gotcha: run scripts as `python -m scripts.<name>` from `backend/`, not `python scripts/x.py` (see D-009).

## Connecting your own Cyberwave account

You only need this for the Cyberwave scripts; tests and dev use the mock robot. The scripts currently point at **Siddharth's** twin and environment, so swap in your own:

**1. API key.** In Cyberwave, go to **Profile → API Tokens** and create a token. Put it in `backend/.env`, which is gitignored; never commit it:
```
CYBERWAVE_API_KEY=your_token_here
# Only if your token covers more than one workspace:
CYBERWAVE_WORKSPACE_ID=your_workspace_uuid
```
The SDK reads the **shell environment**, not `.env`, so load it into each new terminal:
```bash
cd backend && set -a; source .env; set +a
```

**2. Create a Go2 twin.** Run this once. It also creates a "Quickstart Environment" in your account if you don't have one:
```bash
uv run python -c "from cyberwave import Cyberwave; cw=Cyberwave(); a=next(a for a in cw.assets.list() if a.registry_id=='unitree/go2'); t=cw.twin(a.uuid); print('twin', t.uuid, 'env', t.environment_id); cw.disconnect()"
```
This uses the asset UUID because `cw.twin("unitree/go2")` can falsely report "not found" (D-006). Run it **once**: every `cw.twin(<asset>)` call creates a *new* twin. To find IDs later without creating anything, run `uv run python -m scripts.list_twins`, which prints `twin uuid | name | environment uuid`.

**3. Replace the IDs in the scripts:**

| File | Line | Replace with |
|---|---|---|
| `backend/scripts/cyberwave_reposition_proof.py` | 3: `TWIN_ID = "03a3e4d0-…"` | your twin uuid |
| `backend/scripts/cyberwave_proof.py` | 8: `environment_id="8fa26b4e-…"` | your environment uuid |
| `backend/scripts/cyberwave_proof.py` | 10: `twin_id="03a3e4d0-…"` | your twin uuid |

**4. Check it works.** Open your environment in the browser, then run:
```bash
uv run python -m scripts.cyberwave_reposition_proof
```
You should see `PROOF OK`, and the Go2 jumps to (1.5, -0.5) in the browser.

Two notes on the other proof script:
- **Credits:** `cyberwave_proof.py` uses `affect("sim")`, which starts a **billable MuJoCo instance** (about 0.01 credits/min, capped at 60 s). The reposition proof costs no simulation credits.
- **Expected result:** `cyberwave_proof.py` tests locomotion, which is still unresolved (D-006), so expect it to stop at "Still no pose".

## Done

**Milestone 0, foundations**
- Scaffold, FalkorDB round-trip, and test fixtures that give each test its own graph.
- Graph model v1.
- Mock robot adapter.

**Cyberwave**
- The SDK is integrated as far as auth, twin creation and MQTT.
- Locomotion from the SDK didn't move the robot, in either playground or MuJoCo, so that's still unresolved and is an open question for the Cyberwave team (D-006).
- What works is twin *repositioning* via `edit_position`, confirmed by a REST readback (D-007). We describe it honestly as repositioning, not walking.

**Milestone 1, vertical slice**
- Graph seeded from scenario YAML; observations stored with provenance and per-property freshness.
- Location-gated sensing; each step's effect verified by a fresh observation.
- A stuck valve gets acked but fails verification.

**Milestone 2, connected consequences (D-013)**
- Multi-hop impact trace: which supplies feed machine A, who shares them (machine B), which services are critical (line_a).
- `capacity.py` checks supply against demand from graph topology and evidence.
- **"Isolate primary now" is rejected:** "available 0 < demand 7 … would cut critical service line_a".
- `healthy_5`: the standby only has 5 units, so Ripple sheds machine B first, then restores.
- Recovery is confirmed by observed header flow, not assumed.

**Milestone 3, evidence-driven planning (D-014)**
- Per-incident fault hypotheses with `SUPPORTS` / `CONTRADICTS` evidence links.
- A **decision relevance score** ranks inspection points. The robot only travels when a preferred plan is still undecided, and only to points that could change the decision.
- Hop-by-hop routing over `ADJACENT_TO` with FalkorDB's `algo.SPpaths`.
- Stale evidence is detected and not trusted.

**Results, same code and same graph** (5 scenarios, 35 tests):

| Scenario | Ripple chooses | Outcome |
|---|---|---|
| `healthy_8` | activate standby → open bypass → isolate primary | recovered (flow 8 ≥ 7) |
| `healthy_5` | shed B → activate standby → open bypass → isolate primary | recovered (flow 5 ≥ 4) |
| `standby_down` | shed B (degraded operation) | **not** recovered: machine A unserved, reported honestly |
| `stale_valve` | restore via standby; the hour-old "bypass open" log is ignored as stale | recovered |
| `stuck_valve` | restore via standby; the bypass is acked but doesn't move | failure caught by verification |

## Next steps

| Milestone | What | Notes |
|---|---|---|
| **M4: branches + explanations** | Evaluate each candidate plan in a `GRAPH.COPY` branch; the transition model writes `source:"predicted"` observations there (DP5); run the same validation queries in the branch; always delete branches (`graph/branching.py`); persist a `Decision` (the `create_decision` query is ready); `agent/explanations.py` builds text only from `decision_trace` | Replaces the in-memory predicted overlay (`transition_model.with_effects`) and the fixed candidate list (D-012) |
| **M5: eval, UI, demo** | 3 configs (local baseline / graph without inspection / full Ripple) × 6 scenarios (`new_load` still to write); topology-change test (add a load in YAML, no code change, decision changes); FastAPI routes + WebSocket; React UI (facility view, subgraph, decision trace, fault controls); README; demo video | Optional: `CyberwaveRobotAdapter` via `edit_position` for a live 3D view (D-007) |

## Known gaps

- Candidate plans are still a fixed, preference-ordered list in `agent/orchestrator.py` (D-012/D-013). M4 should generate and evaluate them through graph branches.
- Plan validation uses an in-memory overlay of predicted effects; M4 moves this into `GRAPH.COPY` branches.
- The relevance-score weights (3 / 1 / 0.5 / 0.05) are hand-set. Be ready to justify them as a transparent heuristic.
- Still to write: the `new_load` scenario; FastAPI routes; the LLM agent layer / MCP; the frontend.
