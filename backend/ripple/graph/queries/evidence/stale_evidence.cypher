// Purpose:    Decision-relevant evidence (properties named by evidence Conditions) that is missing or older
//             than its per-property freshness window.
// Parameters: $now, $windows (map property -> seconds, from evidence/freshness.py), $default_window
// Returns:    asset_id, property, last_seen (null = never observed), window
// Used by:    ripple.graph.repository.stale_evidence (M3)
MATCH (c:Condition {kind: 'evidence'})-[:CONDITION_ON]->(a:Asset)
OPTIONAL MATCH (o:Observation {property: c.property})-[:ABOUT]->(a)
WITH a, c.property AS property, max(o.observed_at) AS last_seen
WITH a, property, last_seen, coalesce($windows[property], $default_window) AS window
WHERE last_seen IS NULL OR $now - last_seen > window
RETURN DISTINCT a.id AS asset_id, property, last_seen, window
ORDER BY asset_id, property
