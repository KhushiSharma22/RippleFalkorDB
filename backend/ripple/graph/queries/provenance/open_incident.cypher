// Purpose:    Open an Incident concerning the asset that raised the alarm.
// Parameters: $id, $asset_id, $now
// Returns:    id
// Used by:    ripple.graph.repository.open_incident
MATCH (a:Asset {id: $asset_id})
CREATE (i:Incident {id: $id, opened_at: $now, status: 'open'})-[:CONCERNS]->(a)
RETURN i.id AS id
