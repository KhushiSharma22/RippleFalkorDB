// Purpose:    Everything an asset depends on upstream along FEEDS (reverse multi-hop), nearest first.
//             "Ripple traces its cooling dependencies" step of the incident sequence.
// Parameters: $asset_id
// Returns:    asset_id, labels, hops
// Used by:    ripple.graph.repository.upstream_assets (M2)
MATCH p = (u:Asset)-[:FEEDS*1..]->(:Asset {id: $asset_id})
RETURN u.id AS asset_id, labels(u) AS labels, min(length(p)) AS hops
ORDER BY hops, asset_id
