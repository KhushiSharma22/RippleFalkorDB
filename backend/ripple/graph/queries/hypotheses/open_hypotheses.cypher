// Purpose:    Open hypotheses for an incident with counts of supporting / contradicting observations (evidence, not causation).
// Parameters: $incident_id
// Returns:    hypothesis_id, name, supporting, contradicting
// Used by:    ripple.graph.repository.open_hypotheses (M3)
MATCH (:Incident {id: $incident_id})-[:HAS_HYPOTHESIS]->(h:Hypothesis {status: 'open'})
OPTIONAL MATCH (s:Observation)-[:SUPPORTS]->(h)
WITH h, count(DISTINCT s) AS supporting
OPTIONAL MATCH (c:Observation)-[:CONTRADICTS]->(h)
RETURN h.id AS hypothesis_id, h.name AS name, supporting, count(DISTINCT c) AS contradicting
ORDER BY supporting DESC, hypothesis_id
