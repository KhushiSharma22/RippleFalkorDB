// Purpose:    Persist one Observation (never overwrite), link it to its asset, producer and incident,
//             and bump the global StateRevision counter.
// Parameters: $id, $asset_id, $property, $value, $unit, $observed_at, $ingested_at, $quality, $source,
//             $mission_id, $produced_by (Sensor/Robot id or null), $incident_id (or null)
// Returns:    id, revision
// Used by:    ripple.graph.repository.insert_observation

MATCH (a:Asset {id: $asset_id})
CREATE (o:Observation {id: $id, property: $property, value: $value, unit: $unit,
                       observed_at: $observed_at, ingested_at: $ingested_at, quality: $quality,
                       source: $source, mission_id: $mission_id})
CREATE (o)-[:ABOUT]->(a)
WITH o
OPTIONAL MATCH (p {id: $produced_by}) WHERE p:Sensor OR p:Robot
FOREACH (_ IN CASE WHEN p IS NULL THEN [] ELSE [1] END | CREATE (o)-[:PRODUCED_BY]->(p))
WITH o
OPTIONAL MATCH (i:Incident {id: $incident_id})
FOREACH (_ IN CASE WHEN i IS NULL THEN [] ELSE [1] END | CREATE (o)-[:DURING]->(i))
WITH o
MERGE (r:StateRevision {id: 'current'})
ON CREATE SET r.n = 0
SET r.n = r.n + 1, r.at = $ingested_at
RETURN o.id AS id, r.n AS revision
