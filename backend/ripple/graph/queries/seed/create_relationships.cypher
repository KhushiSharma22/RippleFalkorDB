// Purpose:    Batch-create relationships of one type between nodes matched by id.
// Parameters: $rows: list of {from, to, props}.
//             {type} is a placeholder filled by seed.py from seed.REL_TYPES only (types can't be parameters).
// Returns:    nothing (callers use QueryResult.relationships_created)
// Used by:    ripple.graph.seed.seed_from_scenario
// Note:       unlabeled MATCH by id is a full scan; acceptable for one-off seeding of ~25 nodes.
UNWIND $rows AS row
MATCH (a {id: row.from}), (b {id: row.to})
CREATE (a)-[e:{type}]->(b) SET e += row.props