// Purpose:    Every asset downstream of a given asset along FEEDS (multi-hop impact), with hop distance.
// Parameters: $asset_id
// Returns:    asset_id, labels, hops (shortest hop count)
// Used by:    ripple.graph.repository.affected_assets (M2)
MATCH p = (:Asset {id: $asset_id})-[:FEEDS*1..]->(d:Asset)
RETURN d.id AS asset_id, labels(d) AS labels, min(length(p)) AS hops
ORDER BY hops, asset_id
