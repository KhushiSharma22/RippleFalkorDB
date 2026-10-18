// Purpose:    Supplies other than the faulted one with a FEEDS path to a target asset, and the valves on that path.
//             A path is reachability, NOT sufficiency: capacity is checked in planning/capacity.py (DP2).
// Parameters: $asset_id (target), $exclude_supply_id (null = return every supply path)
// Returns:    supply_id, nominal_capacity, valves_on_path
// Used by:    ripple.graph.repository.alternate_supplies (M2)
MATCH p = (s:Supply)-[:FEEDS*1..]->(:Asset {id: $asset_id})
WHERE $exclude_supply_id IS NULL OR s.id <> $exclude_supply_id
RETURN s.id AS supply_id, s.nominal_capacity AS nominal_capacity,
       [n IN nodes(p) WHERE n:Valve | n.id] AS valves_on_path
ORDER BY supply_id
