// Purpose:    Copy every HypothesisTemplate into open Hypotheses for an incident, with their EXPECTS patterns
//             and DISTINGUISHED_BY inspection points. Templates are scenario data; hypotheses are per incident.
// Parameters: $incident_id
// Returns:    n (hypotheses created)
// Used by:    ripple.graph.repository.instantiate_hypotheses (M3)
MATCH (i:Incident {id: $incident_id})
MATCH (t:HypothesisTemplate)
CREATE (i)-[:HAS_HYPOTHESIS]->(h:Hypothesis {id: $incident_id + ':' + t.id, template: t.id,
                                             name: t.name, status: 'open'})
WITH h, t
OPTIONAL MATCH (t)-[e:EXPECTS]->(a:Asset)
FOREACH (_ IN CASE WHEN a IS NULL THEN [] ELSE [1] END |
         CREATE (h)-[:EXPECTS {property: e.property, op: e.op, value: e.value}]->(a))
WITH DISTINCT h, t
OPTIONAL MATCH (t)-[:DISTINGUISHED_BY]->(ip:InspectionPoint)
FOREACH (_ IN CASE WHEN ip IS NULL THEN [] ELSE [1] END | CREATE (h)-[:DISTINGUISHED_BY]->(ip))
RETURN count(DISTINCT h) AS n
