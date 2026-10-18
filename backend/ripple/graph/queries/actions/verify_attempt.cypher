// Purpose:    Link an attempt to the Observation that confirmed (or refuted) its effect.
// Parameters: $id, $observation_id, $status ('verified' | 'failed')
// Returns:    status
// Used by:    ripple.graph.repository.verify_attempt
MATCH (x:ExecutionAttempt {id: $id}), (o:Observation {id: $observation_id})
CREATE (x)-[:VERIFIED_BY]->(o)
SET x.status = $status
RETURN x.status AS status
