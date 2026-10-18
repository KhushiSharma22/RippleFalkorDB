// Purpose:    Batch-create nodes that share one label set.
// Parameters: $rows: list of property maps (no "labels" key).
//             {labels} is a placeholder filled by seed.py from seed.NODE_LABELS only (labels can't be parameters).
// Returns:    nothing (callers use QueryResult.nodes_created)
// Used by:    ripple.graph.seed.seed_from_scenario
UNWIND $rows AS row
CREATE (n:{labels})
SET n += row
