"""Action effects on *predicted* state (ours, not the DB's). Predicted != observed.

M2/M3: a lightweight overlay {(asset, property): value} built from each action's declared
AFFECTS edges, used to validate later steps of a plan. M4 replaces the overlay with a
GRAPH.COPY branch holding `source: "predicted"` Observations (DP5).
"""

from typing import Any

from falkordb import Graph

from ripple.evidence.beliefs import Predicted
from ripple.graph import repository


def with_effects(graph: Graph, action_id: str, predicted: Predicted | None = None) -> Predicted:
    """Return a new overlay: `predicted` plus the declared effects of `action_id`."""
    overlay = dict(predicted or {})
    for effect in repository.action_effects(graph, action_id):
        overlay[(effect["asset_id"], effect["property"])] = effect["value"]
    return overlay


def apply_plan(branch: Graph, plan: list[Any]) -> None:
    """Write each step's predicted effects into a branch graph (Milestone 4)."""
    raise NotImplementedError("TODO(siddharth): GRAPH.COPY transition model (Milestone 4)")
