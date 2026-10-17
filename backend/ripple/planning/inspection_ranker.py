"""Decision relevance score: how likely an inspection is to change the chosen plan.

Honest naming: this is a heuristic, not information gain."""

from typing import Any

from falkordb import Graph


def rank_inspections(graph: Graph, incident_id: str) -> list[dict[str, Any]]:
    """Inspection points ordered by decision relevance score (with travel cost)."""
    raise NotImplementedError("TODO(siddharth): decision relevance score")
