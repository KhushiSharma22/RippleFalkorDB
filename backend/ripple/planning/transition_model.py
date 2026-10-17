"""Applies action effects to *predicted* state (ours, not the DB's). Predicted != observed."""

from typing import Any

from falkordb import Graph


def apply_plan(branch: Graph, plan: list[Any]) -> None:
    """Write each step's predicted effects into a branch graph (never the main graph)."""
    raise NotImplementedError("TODO(siddharth): transition model")
