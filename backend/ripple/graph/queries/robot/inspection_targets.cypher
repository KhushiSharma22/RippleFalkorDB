// Purpose:    Location gate for sensing: what can be read at an inspection point, ONLY if the robot is
//             AT the inspection point's location. Empty result = robot not there (invariant #2).
// Parameters: $robot_id, $ip_id
// Returns:    asset_id, property
// Used by:    ripple.graph.repository.inspection_targets (via ripple.simulator.sensors.read)
MATCH (:Robot {id: $robot_id})-[:AT]->(l:Location)<-[:LOCATED_IN]-(ip:InspectionPoint {id: $ip_id})
MATCH (ip)-[i:INSPECTS]->(a:Asset)
RETURN a.id AS asset_id, i.property AS property
ORDER BY a.id, i.property
