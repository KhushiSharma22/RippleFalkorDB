// Purpose:    Inspection points that would discriminate between an incident's open hypotheses, most discriminating first.
// Parameters: $incident_id
// Returns:    ip_id, location_id, hypotheses, n_hypotheses
// Used by:    ripple.graph.repository.distinguishing_inspections (M3)
MATCH (:Incident {id: $incident_id})-[:HAS_HYPOTHESIS]->(h:Hypothesis {status: 'open'})
MATCH (h)-[:DISTINGUISHED_BY]->(ip:InspectionPoint)-[:LOCATED_IN]->(l:Location)
RETURN ip.id AS ip_id, l.id AS location_id, collect(h.id) AS hypotheses, count(h) AS n_hypotheses
ORDER BY n_hypotheses DESC, ip_id
