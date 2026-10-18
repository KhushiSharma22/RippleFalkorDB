// Purpose:    Where can the robot go to observe this asset property? (inspection point + its location)
// Parameters: $asset_id, $property
// Returns:    ip_id, location_id, x, y
// Used by:    ripple.graph.repository.inspection_points_for
MATCH (ip:InspectionPoint)-[:INSPECTS {property: $property}]->(:Asset {id: $asset_id})
MATCH (ip)-[:LOCATED_IN]->(l:Location)
RETURN ip.id AS ip_id, l.id AS location_id, l.x AS x, l.y AS y
ORDER BY ip.id


