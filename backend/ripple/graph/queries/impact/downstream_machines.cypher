// Purpose:    Machines fed (directly or multi-hop) by an asset, with their cooling demand and criticality.
//             Used for the demand side of the capacity check and for service verification.
// Parameters: $asset_id
// Returns:    machine_id, demand, criticality
// Used by:    ripple.graph.repository.downstream_machines (M2)
MATCH (:Asset {id: $asset_id})-[:FEEDS*1..]->(m:Machine)
RETURN DISTINCT m.id AS machine_id, m.demand AS demand, m.criticality AS criticality
ORDER BY machine_id
