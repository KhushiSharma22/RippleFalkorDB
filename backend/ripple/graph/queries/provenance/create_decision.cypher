// Purpose:    Persist a Decision: TRIGGERED_BY incident, one Plan per candidate with CONSIDERED, plus SELECTED
//             or REJECTED {reason}, and BASED_ON the observations used. $plans must be non-empty.
// Parameters: $id, $incident_id, $made_at, $summary, $revision, $plans ([{name, actions, selected, rejected_reason}]), $observation_ids
// Returns:    id
// Used by:    ripple.graph.repository.create_decision (M4)
MATCH (i:Incident {id: $incident_id})
CREATE (d:Decision {id: $id, made_at: $made_at, summary: $summary, revision: $revision})
CREATE (d)-[:TRIGGERED_BY]->(i)
WITH d
UNWIND $plans AS plan
CREATE (p:Plan {id: $id + ':' + plan.name, name: plan.name, actions: plan.actions})
CREATE (d)-[:CONSIDERED]->(p)
FOREACH (_ IN CASE WHEN plan.selected THEN [1] ELSE [] END | CREATE (d)-[:SELECTED]->(p))
FOREACH (_ IN CASE WHEN plan.rejected_reason IS NULL THEN [] ELSE [1] END |
         CREATE (d)-[:REJECTED {reason: plan.rejected_reason}]->(p))
WITH DISTINCT d
OPTIONAL MATCH (o:Observation) WHERE o.id IN $observation_ids
FOREACH (_ IN CASE WHEN o IS NULL THEN [] ELSE [1] END | CREATE (d)-[:BASED_ON]->(o))
RETURN DISTINCT d.id AS id
