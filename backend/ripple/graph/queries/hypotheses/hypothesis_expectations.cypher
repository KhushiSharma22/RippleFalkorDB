// Purpose:    Which open hypotheses of an incident predict something about this (asset, property), and what.
// Parameters: $incident_id, $asset_id, $property
// Returns:    hypothesis_id, op, value
// Used by:    ripple.graph.repository.hypothesis_expectations (M3)
MATCH (:Incident {id: $incident_id})-[:HAS_HYPOTHESIS]->(h:Hypothesis {status: 'open'})
MATCH (h)-[e:EXPECTS {property: $property}]->(:Asset {id: $asset_id})
RETURN h.id AS hypothesis_id, e.op AS op, e.value AS value
ORDER BY hypothesis_id
