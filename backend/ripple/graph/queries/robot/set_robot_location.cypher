// Purpose:    Move the robot's AT edge. Called ONLY after arrival is verified by pose readback (DP4).
// Parameters: $robot_id, $location_id, $now
// Returns:    location_id
// Used by:    ripple.graph.repository.set_robot_location
MATCH (r:Robot {id: $robot_id})-[old:AT]->(:Location)
MATCH (l:Location {id: $location_id})
DELETE old
CREATE (r)-[:AT {since: $now}]->(l)
RETURN l.id AS location_id
