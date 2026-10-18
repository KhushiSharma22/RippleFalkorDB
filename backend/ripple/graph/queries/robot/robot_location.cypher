// Purpose:    The robot's current verified Location (DP4).
// Parameters: $robot_id
// Returns:    location_id, x, y (0 or 1 row)
// Used by:    ripple.graph.repository.robot_location
MATCH (:Robot {id: $robot_id})-[:AT]->(l:Location)
RETURN l.id AS location_id, l.x AS x, l.y AS y
