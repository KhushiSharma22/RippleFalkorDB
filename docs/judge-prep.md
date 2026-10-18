# Judge prep: questions and model answers

> Study sheet, not submission material. Model answers drafted by Claude; rehearse them in your own words.
> Grows with each step. References point to `docs/decisions.md` (D-xxx) and `docs/graph-model.md` (DPx).

## Milestone 0: foundations

### FalkorDB basics (0.1)

**Q: What is a FalkorDB "graph" at the Redis level, and why is there no `database` parameter?**
A: FalkorDB runs as a Redis module. Each graph is a single Redis key, and `select_graph(name)` returns a handle to that key. There's no separate database namespace like Postgres: the main graph, every test graph, and every `GRAPH.COPY` branch are just different keys on one server. So connecting needs only host and port, and isolation means choosing a graph name.

**Q: Why does each test get its own graph instead of a shared one?**
A: Isolation. Each test creates a uniquely named graph (`test_<testname>_<hex>`) and deletes it in a `yield` fixture's teardown, which runs even if the test fails. Tests can't leak state into each other or touch the real `ripple` graph. The `test_` prefix means leftovers from a crash can be swept by pattern. Milestone 4's branches use the same pattern: copy to a uniquely named graph, use it, always delete it.

**Q: Why one shared FalkorDB client?**
A: The client wraps a thread-safe Redis connection pool. A new client per call throws away pooled connections and can exhaust sockets when the API, the orchestrator loop and branch evaluations run at once. `get_db()` is `lru_cache`d, so every caller shares one pool.

**Q: Why parameters (`$id`) instead of formatting values into the query string?**
A: No injection risk, and FalkorDB caches the execution plan per query string, so parameterised queries are parsed once and reused.

### Cyberwave (0.2)

**Q: Did your robot actually walk in Cyberwave?**
A: No, and we say so (D-006, D-007). We integrated the SDK: auth, catalog, twin creation, MQTT, and starting a MuJoCo simulation. Velocity locomotion commands didn't move the Go2 from the SDK in either playground or MuJoCo, and no pose came back. Keyboard teleop in the browser did move it, so we've raised that with the Cyberwave team. What we proved instead is repositioning: `edit_position` moves the twin in the Cyberwave scene, and a separate REST readback confirms the new position. Our Cyberwave adapter uses that and we call it "twin repositioning", not walking. Because both adapters share one interface, real locomotion would only change `move_to`.

**Q: Why isn't `move_to` trusted until a separate readback confirms it?**
A: A command is an intention, not an outcome (invariant #3: predicted ≠ observed). Commands can be dropped. We saw this live: a command was lost while the controller policy was still attaching. So `move_to` returns nothing, and arrival is decided only by reading the pose back and checking it with `arrived(pose, target, tol)`. Only then does the graph's `(:Robot)-[:AT]->(:Location)` edge move (DP4).

### Robot adapter (0.3)

**Q: Why a mock robot at all?**
A: Development, tests and the evaluation (3 configs × 6 scenarios) must be fast, repeatable and not depend on an external service. The mock implements the same `RobotAdapter` Protocol and can inject failures (`fail_next_moves`), which lets us test the verify-and-replan path deterministically. That's hard to do with a real or cloud robot.

**Q: Why doesn't the adapter know about locations or routes?**
A: That would be a second copy of topology outside the graph (invariant #1). Location coordinates live on `Location` nodes, routes come from `ADJACENT_TO` queries, and the adapter only receives target coordinates. If you remove FalkorDB, the robot has nowhere to go.

### Graph model (0.4)

**Q (DP1): Why not just store `position: 'open'` on the valve node? It's simpler.**
A: A property only holds the latest value, and it loses *when* it was observed, *who* observed it, and *how reliable* it is. Ripple's decisions depend on exactly that: "the valve was reported open yesterday by a log" is different from "the robot confirmed it open two minutes ago". As `Observation` nodes, each fact keeps time, source and quality. Freshness becomes a query ("latest observation older than its window"), and there's one source of truth for state. Static design facts (nominal capacity, demand, criticality) stay as properties because they don't change during an incident.

**Q (DP5): Why do hypothetical branches write `Observation`s instead of updating properties in the copy?**
A: Two reasons. (1) The same evaluation queries run unchanged on the main graph and on every branch, because state is always read the same way (latest Observation). (2) Predicted facts are labelled `source: "predicted"`, so they can never be confused with real evidence, and the whole branch is deleted after evaluation anyway. Also, `GRAPH.COPY` is a snapshot, not a physics simulation: our transition model writes the predicted effects.

**Q (DP2): Why both `FEEDS` and `CONNECTED_TO`?**
A: A pipe connection doesn't mean sufficient cooling. `CONNECTED_TO` records physical plumbing. `FEEDS` is the directed operational flow path (non-return assumed) used for impact traversal. Whether flow is enough is computed in `planning/capacity.py` from capacities fetched from the graph. A path is never treated as proof of supply.

**Q (DP3): Why isn't `InspectionPoint` an `Asset`?**
A: It isn't equipment: it doesn't feed, fail or carry load. If it were an `Asset`, impact queries like `MATCH (a:Asset)` would return gauges as affected equipment. As its own label it links cleanly: `(:InspectionPoint)-[:INSPECTS {property}]->(:Asset)` and `-[:LOCATED_IN]->(:Location)`.

**Q (DP4): How does location-gated sensing use the graph?**
A: The robot's verified position is an edge, `(:Robot)-[:AT]->(:Location)`. A reading is allowed only if `(robot)-[:AT]->(loc)<-[:LOCATED_IN]-(ip)-[:INSPECTS]->(asset)` matches. The edge moves only after verified arrival, so the robot can't "sense" from somewhere it was merely commanded to go.

**Q: How do you prove the graph matters (the "remove FalkorDB" test)?**
A: Topology, dependencies, prerequisites, evidence and robot access all come only from Cypher queries in `graph/queries/`, and there's no in-memory mirror. Remove FalkorDB and the planner has no topology, the validator has no prerequisites, and the robot has no locations. The planned topology-change test adds a new load to the graph without code changes and shows the chosen intervention changing.

## Milestone 1: vertical slice

**Q: Show me that the robot's observation changes the decision.**
A: `healthy_8` and `standby_down` share the exact same graph and code; only the hidden truth differs. In both, the validator finds no standby health evidence (`activate_standby REQUIRES c_standby_healthy CONDITION_ON standby_supply`), so the robot drives to `ip_standby_pump` and reads it. Healthy gives `restore_via_standby`; failed gives `shed_noncritical_load`. Test: `test_observation_is_what_changes_the_decision`.

**Q: How do you stop the agent from cheating by reading the simulator's truth?**
A: Three layers. (1) The orchestrator never imports the simulator: it gets `sense` and `actuate` callables, and an AST test fails the build if agent/planning/evidence import `ripple.simulator`. (2) `sensors.read` is the only path from truth to evidence, and it's location-gated *in Cypher*: `inspection_targets` returns rows only if `(robot)-[:AT]->(loc)<-[:LOCATED_IN]-(ip)`. (3) The `AT` edge moves only after pose readback confirms arrival.

**Q: What's the difference between an ack and success?**
A: Every effect creates an `ExecutionAttempt` (status `sent`), the controller's ack sets `acked`, and only a fresh observation from re-inspection sets `verified` or `failed` via `VERIFIED_BY`. Test `test_stuck_valve_is_caught_by_verification_not_by_ack`: the bypass is stuck, the command is acked, but the observation shows it still closed, so the attempt fails and recovery isn't claimed.

**Q: Why does `latest_observation` define "current state"?**
A: DP1: state lives only in Observations. The query takes the newest Observation ABOUT the asset for that property (`ORDER BY observed_at DESC LIMIT 1`). The validator then applies per-property freshness: a day-old log is "stale", so it triggers an inspection instead of being trusted.

**Q: Your candidate plans are a hardcoded list. Isn't that the opposite of graph-driven?**
A: For M1, yes, and we say so (D-012). M1 proves one thing: evidence changes the action. Everything the decision *depends on* already comes from the graph: prerequisites, inspection locations, coordinates, robot position, effects. Graph-driven candidates, multi-hop impact and `GRAPH.COPY` branch evaluation replace the list in M2–M4.
