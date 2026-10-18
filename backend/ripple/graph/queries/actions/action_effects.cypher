// Purpose:    Declared effects of an Action (what it should change, on which asset).
// Parameters: $action_id
// Returns:    asset_id, property, value
// Used by:    ripple.graph.repository.action_effects
MATCH (:Action {id: $action_id})-[e:AFFECTS]->(a:Asset)
RETURN a.id AS asset_id, e.property AS property, e.value AS value
ORDER BY a.id, e.property
