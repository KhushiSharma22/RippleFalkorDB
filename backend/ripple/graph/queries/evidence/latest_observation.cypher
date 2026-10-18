// Purpose:    Current belief about one asset property = its most recent Observation (DP1).
// Parameters: $asset_id, $property
// Returns:    id, value, unit, observed_at, quality, source (0 or 1 row)
// Used by:    ripple.graph.repository.latest_observation
MATCH (o:Observation {property: $property})-[:ABOUT]->(:Asset {id: $asset_id})
RETURN o.id AS id, o.value AS value, o.unit AS unit, o.observed_at AS observed_at,
       o.quality AS quality, o.source AS source
ORDER BY o.observed_at DESC
LIMIT 1
