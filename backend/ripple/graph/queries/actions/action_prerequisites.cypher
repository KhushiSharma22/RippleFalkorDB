// Purpose:    Every Condition an Action REQUIRES, with the asset each condition is on.
// Parameters: $action_id
// Returns:    condition_id, kind, property, op, value, check, asset_id
// Used by:    ripple.graph.repository.action_prerequisites
MATCH (:Action {id: $action_id})-[:REQUIRES]->(c:Condition)-[:CONDITION_ON]->(a:Asset)
RETURN c.id AS condition_id, c.kind AS kind, c.property AS property, c.op AS op,
       c.value AS value, c.check AS check, a.id AS asset_id
ORDER BY c.id
