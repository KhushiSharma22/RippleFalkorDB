// Purpose:    Link an Observation to a Hypothesis as SUPPORTS or CONTRADICTS (evidence, not causation).
//             A contradicted hypothesis is marked 'rejected'. Relationship types can't be parameters,
//             so both branches are written and FOREACH/CASE picks one.
// Parameters: $observation_id, $hypothesis_id, $supports (bool), $rule
// Returns:    status
// Used by:    ripple.graph.repository.record_hypothesis_evidence (M3)
MATCH (o:Observation {id: $observation_id}), (h:Hypothesis {id: $hypothesis_id})
FOREACH (_ IN CASE WHEN $supports THEN [1] ELSE [] END | CREATE (o)-[:SUPPORTS {rule: $rule}]->(h))
FOREACH (_ IN CASE WHEN $supports THEN [] ELSE [1] END |
         CREATE (o)-[:CONTRADICTS {rule: $rule}]->(h) SET h.status = 'rejected')
RETURN h.status AS status
