// Purpose:    Record that a command was SENT (not that it worked): invariant #3.
// Parameters: $id, $action_id, $incident_id, $asset_id, $property, $expected, $sent_at
// Returns:    id
// Used by:    ripple.graph.repository.create_attempt
MATCH (act:Action {id: $action_id}), (i:Incident {id: $incident_id})
CREATE (x:ExecutionAttempt {id: $id, asset_id: $asset_id, property: $property,
                            expected: $expected, sent_at: $sent_at, status: 'sent'})
CREATE (x)-[:ATTEMPTS]->(act), (x)-[:DURING]->(i)
RETURN x.id AS id
