# Query index

Every Cypher query the product depends on. Source of truth: `backend/ripple/graph/queries/`.
Runtime queries run only through `ripple/graph/repository.py` (enforced by `tests/test_architecture.py`).

| file | answers | used by | status |
|---|---|---|---|
| seed/create_nodes.cypher | batch-create nodes of one whitelisted label set | `seed.seed_from_scenario` | M1 ✅ |
| seed/create_relationships.cypher | batch-create edges of one whitelisted type, matched by id | `seed.seed_from_scenario` | M1 ✅ |
| evidence/insert_observation.cypher | persist an Observation + ABOUT/PRODUCED_BY/DURING, bump StateRevision | `repository.insert_observation` | M1 |
| evidence/latest_observation.cypher | current belief = latest observation of (asset, property) | `repository.latest_observation` | M1 |
| evidence/inspection_points_for.cypher | where can the robot observe (asset, property)? | `repository.inspection_points_for` | M1 |
| actions/action_prerequisites.cypher | conditions an action REQUIRES + asset each is ON | `repository.action_prerequisites` | M1 |
| actions/action_effects.cypher | declared AFFECTS of an action | `repository.action_effects` | M1 |
| actions/create_attempt.cypher | record a command was SENT | `repository.create_attempt` | M1 |
| actions/update_attempt.cypher | record the ack (receipt, not effect) | `repository.update_attempt` | M1 |
| actions/verify_attempt.cypher | link attempt to verifying observation | `repository.verify_attempt` | M1 |
| robot/robot_location.cypher | robot's verified Location | `repository.robot_location` | M1 |
| robot/set_robot_location.cypher | move AT edge after verified arrival | `repository.set_robot_location` | M1 |
| robot/inspection_targets.cypher | location gate: readable (asset, property) only if robot is there | `repository.inspection_targets` → `sensors.read` | M1 |
| provenance/open_incident.cypher | open Incident CONCERNS alarming asset | `repository.open_incident` | M1 |
| impact/affected_assets.cypher | multi-hop downstream impact | `repository.affected_assets` | M2 |
| impact/alternate_supplies.cypher | supplies that can reach an asset | `repository.alternate_supplies` | M2 |
| impact/critical_services_affected.cypher | critical services hit | `repository.critical_services_affected` | M2 |
| evidence/stale_evidence.cypher | decision-relevant stale/missing evidence | `repository.stale_evidence` | M3 |
| hypotheses/open_hypotheses.cypher | unresolved hypotheses | `repository.open_hypotheses` | M3 |
| hypotheses/distinguishing_inspections.cypher | inspections that discriminate hypotheses | `repository.distinguishing_inspections` | M3 |
| robot/route_to_inspection_point.cypher | cheapest ADJACENT_TO route | `repository.route_to_inspection_point` | M3 |
| provenance/create_decision.cypher | persist Decision provenance | `repository.create_decision` | M4 |
| provenance/decision_trace.cypher | decision trace for explanations | `repository.decision_trace` | M4 |
