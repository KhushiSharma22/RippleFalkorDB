// Purpose:    Cheapest ADJACENT_TO route (by cost) from the robot's location to an inspection point,
//             using FalkorDB's built-in algo.SPpaths (undirected). Same-location case returns a 1-node route.
// Parameters: $robot_id, $ip_id
// Returns:    locations, waypoints ([x, y] per location), cost (empty = unreachable)
// Used by:    ripple.graph.repository.route_to_inspection_point (M3)
MATCH (:Robot {id: $robot_id})-[:AT]->(start:Location)
MATCH (:InspectionPoint {id: $ip_id})-[:LOCATED_IN]->(goal:Location)
WHERE start = goal
RETURN [start.id] AS locations, [[start.x, start.y]] AS waypoints, 0.0 AS cost
UNION
MATCH (:Robot {id: $robot_id})-[:AT]->(start:Location)
MATCH (:InspectionPoint {id: $ip_id})-[:LOCATED_IN]->(goal:Location)
WHERE start <> goal
CALL algo.SPpaths({sourceNode: start, targetNode: goal, relTypes: ['ADJACENT_TO'],
                   weightProp: 'cost', relDirection: 'both', pathCount: 1})
YIELD path, pathWeight
RETURN [n IN nodes(path) | n.id] AS locations, [n IN nodes(path) | [n.x, n.y]] AS waypoints,
       pathWeight AS cost
