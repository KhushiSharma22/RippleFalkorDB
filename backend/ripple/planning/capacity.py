"""Allocation math over topology fetched from the graph (M2).

Physical connection (CONNECTED_TO / a FEEDS path) != operational sufficiency. A supply path
contributes capacity only if the supply is healthy and running, every valve on the path is
open, and its *observed* capacity is known: all judged from fresh evidence (or a planning
prediction). Topology comes from repository queries; there is no in-memory topology mirror.

Decision-driven: evidence is requested only when it could change the answer. A path with any
known-false factor contributes 0 without further inspection; if known capacity already covers
demand, unknown paths don't matter; if even optimistic (nominal) capacity can't cover demand,
the check fails without inspection.
"""

from dataclasses import dataclass, field

from falkordb import Graph

from ripple.evidence.beliefs import Predicted, belief
from ripple.graph import repository
from ripple.planning.transition_model import with_effects


@dataclass
class CapacityResult:
    ok: bool
    available: float  # capacity confirmed by evidence/prediction
    demand: float
    violations: list[str] = field(default_factory=list)
    missing: list[tuple[str, str]] = field(default_factory=list)


def _path_status(
    graph: Graph, path: dict, now: float, overlay: Predicted
) -> tuple[str, float, list[tuple[str, str]]]:
    """('supplying' | 'off' | 'unknown', capacity or upper bound, missing evidence) for one path."""
    supply = path["supply_id"]
    gates = [(supply, "health", lambda v: v == "ok"), (supply, "running", lambda v: v is True)]
    gates += [(valve, "position", lambda v: v == "open") for valve in path["valves_on_path"]]
    missing: list[tuple[str, str]] = []
    for asset_id, prop, passes in gates:
        b = belief(graph, asset_id, prop, now, overlay)
        if b.usable and not passes(b.value):
            return "off", 0.0, []
        if not b.usable:
            missing.append((asset_id, prop))
    cap = belief(graph, supply, "capacity", now, overlay)
    if not cap.usable:
        missing.append((supply, "capacity"))
    capacity = float(cap.value) if cap.usable else float(path["nominal_capacity"])
    return ("unknown" if missing else "supplying"), capacity, missing


def _demand(
    graph: Graph, header_id: str, now: float, overlay: Predicted
) -> tuple[float, list[str]]:
    """Total demand of machines believed running. No fresh evidence = assume running (conservative)."""
    total, running = 0.0, []
    for m in repository.downstream_machines(graph, header_id):
        b = belief(graph, m["machine_id"], "running", now, overlay)
        if not b.usable or b.value is True:
            total += float(m["demand"])
            running.append(m["machine_id"])
    return total, running


def demand_within_capacity(
    graph: Graph,
    header_id: str,
    now: float,
    action_id: str | None = None,
    predicted: Predicted | None = None,
) -> CapacityResult:
    """Will supply to `header_id` cover the demand of its running machines *after* `action_id`?"""
    overlay = with_effects(graph, action_id, predicted) if action_id else dict(predicted or {})
    known, optimistic, missing = 0.0, 0.0, []
    for path in repository.alternate_supplies(graph, header_id):
        status, capacity, path_missing = _path_status(graph, path, now, overlay)
        if status == "supplying":
            known += capacity
        elif status == "unknown":
            optimistic += capacity
            missing += [m for m in path_missing if m not in missing]

    demand, running = _demand(graph, header_id, now, overlay)
    if known >= demand:
        return CapacityResult(True, known, demand)
    if known + optimistic >= demand:
        return CapacityResult(False, known, demand, missing=missing)

    at_risk = [
        f"{s['service_id']} ({s['machine_id']})"
        for s in repository.critical_services_affected(graph, header_id)
        if s["machine_id"] in running
    ]
    when = f"after {action_id}" if action_id else "now"
    message = f"capacity {when}: available {known:g} < demand {demand:g} ({', '.join(running)})"
    if at_risk:
        message += f"; would cut critical service {', '.join(at_risk)}"
    return CapacityResult(False, known, demand, violations=[message])
