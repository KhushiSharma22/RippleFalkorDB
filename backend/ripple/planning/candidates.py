"""Bounded candidate action-sequence generation (few action types, short sequences)."""

from typing import Any

from falkordb import Graph


def generate_candidates(graph: Graph, incident_id: str, max_len: int = 3) -> list[list[Any]]:
    """Candidate plans built from Actions in the graph, length <= max_len."""
    raise NotImplementedError("TODO(siddharth): candidate generation")
