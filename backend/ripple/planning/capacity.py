"""Allocation math over topology fetched from the graph.

Physical connection (CONNECTED_TO) != operational sufficiency. Topology comes from
repository queries; no in-memory topology mirror."""

from typing import Any


def allocate(topology_rows: list[dict[str, Any]]) -> dict[str, float]:
    """Given supply/flow/demand rows from the graph, return delivered units per machine."""
    raise NotImplementedError("TODO(siddharth): capacity allocation")
