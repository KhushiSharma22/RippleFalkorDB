// Purpose:    Critical services provided by machines downstream of a given asset.
// Parameters: $asset_id
// Returns:    service_id, name, machine_id, demand
// Used by:    ripple.graph.repository.critical_services_affected (M2)
MATCH (:Asset {id: $asset_id})-[:FEEDS*1..]->(m:Machine)-[:PROVIDES_SERVICE]->(s:Service)
WHERE s.critical = true
RETURN DISTINCT s.id AS service_id, s.name AS name, m.id AS machine_id, m.demand AS demand
ORDER BY service_id
