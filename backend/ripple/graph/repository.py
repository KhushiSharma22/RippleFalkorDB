"""Typed functions that run named queries. The ONLY module that executes runtime Cypher.

Every function maps 1:1 to a file in graph/queries/ (see docs/queries.md). Rows come back as
dicts keyed by the query's RETURN aliases.
"""

from typing import Any

from falkordb import Graph

from ripple.evidence.models import Observation
from ripple.graph.query_loader import load_query

Row = dict[str, Any]


def _run(
    graph: Graph, name: str, params: dict[str, Any] | None = None, *, write: bool
) -> list[Row]:
    query = load_query(name)
    result = graph.query(query, params) if write else graph.ro_query(query, params)
    columns = [h[1] for h in result.header]
    return [dict(zip(columns, row, strict=True)) for row in result.result_set]


def _one(rows: list[Row]) -> Row | None:
    return rows[0] if rows else None


# --- evidence -------------------------------------------------------------------
def insert_observation(graph: Graph, observation: Observation) -> int:
    """Persist an Observation with provenance; return the new StateRevision number."""
    rows = _run(graph, "evidence/insert_observation", observation.model_dump(), write=True)
    if not rows:
        raise ValueError(f"Unknown asset {observation.asset_id!r} for observation {observation.id}")
    return int(rows[0]["revision"])


def latest_observation(graph: Graph, asset_id: str, prop: str) -> Row | None:
    """Most recent observation of `prop` on `asset_id`, or None if never observed."""
    return _one(
        _run(
            graph,
            "evidence/latest_observation",
            {"asset_id": asset_id, "property": prop},
            write=False,
        )
    )


def inspection_points_for(graph: Graph, asset_id: str, prop: str) -> list[Row]:
    """Inspection points (with location and coordinates) that can observe `prop` on `asset_id`."""
    params = {"asset_id": asset_id, "property": prop}
    return _run(graph, "evidence/inspection_points_for", params, write=False)


def stale_evidence(graph: Graph, incident_id: str, now: float) -> list[Row]:
    """Decision-relevant evidence older than its freshness window. Query: evidence/stale_evidence."""
    raise NotImplementedError("TODO(siddharth): stale_evidence (Milestone 3)")


# --- actions --------------------------------------------------------------------
def action_prerequisites(graph: Graph, action_id: str) -> list[Row]:
    """Conditions an action requires, with the asset each is on."""
    return _run(graph, "actions/action_prerequisites", {"action_id": action_id}, write=False)


def action_effects(graph: Graph, action_id: str) -> list[Row]:
    """Declared effects (asset, property, value) of an action."""
    return _run(graph, "actions/action_effects", {"action_id": action_id}, write=False)


def create_attempt(
    graph: Graph,
    attempt_id: str,
    action_id: str,
    incident_id: str,
    asset_id: str,
    prop: str,
    expected: Any,
    sent_at: float,
) -> None:
    """Record that a command was sent (status 'sent')."""
    params = {
        "id": attempt_id,
        "action_id": action_id,
        "incident_id": incident_id,
        "asset_id": asset_id,
        "property": prop,
        "expected": expected,
        "sent_at": sent_at,
    }
    if not _run(graph, "actions/create_attempt", params, write=True):
        raise ValueError(f"Unknown action {action_id!r} or incident {incident_id!r}")


def update_attempt(graph: Graph, attempt_id: str, status: str, ack_at: float) -> None:
    """Record the command acknowledgement ('acked' or 'rejected')."""
    _run(
        graph,
        "actions/update_attempt",
        {"id": attempt_id, "status": status, "ack_at": ack_at},
        write=True,
    )


def verify_attempt(graph: Graph, attempt_id: str, observation_id: str, status: str) -> None:
    """Link an attempt to the observation that verified ('verified') or refuted ('failed') it."""
    params = {"id": attempt_id, "observation_id": observation_id, "status": status}
    _run(graph, "actions/verify_attempt", params, write=True)


# --- robot ----------------------------------------------------------------------
def robot_location(graph: Graph, robot_id: str) -> Row | None:
    """Current verified Location of the robot."""
    return _one(_run(graph, "robot/robot_location", {"robot_id": robot_id}, write=False))


def set_robot_location(graph: Graph, robot_id: str, location_id: str, now: float) -> None:
    """Move the robot's AT edge. Call only after verified arrival."""
    params = {"robot_id": robot_id, "location_id": location_id, "now": now}
    if not _run(graph, "robot/set_robot_location", params, write=True):
        raise ValueError(f"Unknown robot {robot_id!r} or location {location_id!r}")


def inspection_targets(graph: Graph, robot_id: str, ip_id: str) -> list[Row]:
    """(asset, property) readable at `ip_id`; empty unless the robot is AT its location."""
    return _run(
        graph, "robot/inspection_targets", {"robot_id": robot_id, "ip_id": ip_id}, write=False
    )


def route_to_inspection_point(graph: Graph, robot_id: str, inspection_point_id: str) -> Row | None:
    """Cheapest ADJACENT_TO route to an inspection point. Query: robot/route_to_inspection_point."""
    raise NotImplementedError("TODO(siddharth): route_to_inspection_point (Milestone 3)")


# --- impact (Milestone 2) ---------------------------------------------------------
def affected_assets(graph: Graph, asset_id: str) -> list[Row]:
    """Assets downstream of `asset_id` (multi-hop). Query: impact/affected_assets."""
    raise NotImplementedError("TODO(siddharth): affected_assets (Milestone 2)")


def alternate_supplies(graph: Graph, asset_id: str) -> list[Row]:
    """Supplies that can physically reach `asset_id`. Query: impact/alternate_supplies."""
    raise NotImplementedError("TODO(siddharth): alternate_supplies (Milestone 2)")


def critical_services_affected(graph: Graph, asset_id: str) -> list[Row]:
    """Critical services lost if `asset_id` stops. Query: impact/critical_services_affected."""
    raise NotImplementedError("TODO(siddharth): critical_services_affected (Milestone 2)")


# --- hypotheses (Milestone 3) -----------------------------------------------------
def open_hypotheses(graph: Graph, incident_id: str) -> list[Row]:
    """Hypotheses not yet resolved for an incident. Query: hypotheses/open_hypotheses."""
    raise NotImplementedError("TODO(siddharth): open_hypotheses (Milestone 3)")


def distinguishing_inspections(graph: Graph, incident_id: str) -> list[Row]:
    """Inspection points that discriminate between open hypotheses."""
    raise NotImplementedError("TODO(siddharth): distinguishing_inspections (Milestone 3)")


# --- provenance -----------------------------------------------------------------
def open_incident(graph: Graph, incident_id: str, asset_id: str, now: float) -> str:
    """Create an Incident concerning the alarming asset; return its id."""
    params = {"id": incident_id, "asset_id": asset_id, "now": now}
    rows = _run(graph, "provenance/open_incident", params, write=True)
    if not rows:
        raise ValueError(f"Unknown asset {asset_id!r}")
    return rows[0]["id"]


def create_decision(graph: Graph, decision: Any) -> str:
    """Persist a Decision with CONSIDERED/REJECTED/SELECTED/BASED_ON edges (Milestone 4)."""
    raise NotImplementedError("TODO(siddharth): create_decision (Milestone 4)")


def decision_trace(graph: Graph, decision_id: str) -> list[Row]:
    """Full provenance trace of a Decision (Milestone 4)."""
    raise NotImplementedError("TODO(siddharth): decision_trace (Milestone 4)")
