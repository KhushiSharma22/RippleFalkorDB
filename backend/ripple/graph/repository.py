"""Typed functions that run named queries. The ONLY module that executes Cypher.

Return types are placeholders; TODO(siddharth): replace dict rows with Pydantic models."""

from typing import Any

from falkordb import Graph

Row = dict[str, Any]


# --- impact -----------------------------------------------------------------
def affected_assets(graph: Graph, asset_id: str) -> list[Row]:
    """Assets downstream of `asset_id` (multi-hop). Query: impact/affected_assets."""
    raise NotImplementedError("TODO(siddharth): affected_assets")


def alternate_supplies(graph: Graph, asset_id: str) -> list[Row]:
    """Supplies that can physically reach `asset_id`. Query: impact/alternate_supplies."""
    raise NotImplementedError("TODO(siddharth): alternate_supplies")


def critical_services_affected(graph: Graph, asset_id: str) -> list[Row]:
    """Critical services lost if `asset_id` stops. Query: impact/critical_services_affected."""
    raise NotImplementedError("TODO(siddharth): critical_services_affected")


# --- evidence ---------------------------------------------------------------
def insert_observation(graph: Graph, observation: Any) -> str:
    """Persist an Observation with provenance; return its id. Query: evidence/insert_observation."""
    raise NotImplementedError("TODO(siddharth): insert_observation")


def latest_observation(graph: Graph, asset_id: str, prop: str) -> Row | None:
    """Most recent observation of `prop` on `asset_id`. Query: evidence/latest_observation."""
    raise NotImplementedError("TODO(siddharth): latest_observation")


def stale_evidence(graph: Graph, incident_id: str, now: float) -> list[Row]:
    """Decision-relevant evidence older than its freshness window. Query: evidence/stale_evidence."""
    raise NotImplementedError("TODO(siddharth): stale_evidence")


# --- hypotheses -------------------------------------------------------------
def open_hypotheses(graph: Graph, incident_id: str) -> list[Row]:
    """Hypotheses not yet resolved for an incident. Query: hypotheses/open_hypotheses."""
    raise NotImplementedError("TODO(siddharth): open_hypotheses")


def distinguishing_inspections(graph: Graph, incident_id: str) -> list[Row]:
    """Inspection points that discriminate between open hypotheses. Query: hypotheses/distinguishing_inspections."""
    raise NotImplementedError("TODO(siddharth): distinguishing_inspections")


# --- actions ----------------------------------------------------------------
def action_prerequisites(graph: Graph, action_id: str) -> list[Row]:
    """Conditions an action requires, with the assets they're on. Query: actions/action_prerequisites."""
    raise NotImplementedError("TODO(siddharth): action_prerequisites")


def action_effects(graph: Graph, action_id: str) -> list[Row]:
    """Declared effects of an action on assets. Query: actions/action_effects."""
    raise NotImplementedError("TODO(siddharth): action_effects")


# --- robot ------------------------------------------------------------------
def robot_location(graph: Graph, robot_id: str) -> Row | None:
    """Current Location of the robot. Query: robot/robot_location."""
    raise NotImplementedError("TODO(siddharth): robot_location")


def route_to_inspection_point(graph: Graph, robot_id: str, inspection_point_id: str) -> Row | None:
    """Cheapest ADJACENT_TO route to an inspection point. Query: robot/route_to_inspection_point."""
    raise NotImplementedError("TODO(siddharth): route_to_inspection_point")


# --- provenance -------------------------------------------------------------
def create_decision(graph: Graph, decision: Any) -> str:
    """Persist a Decision with CONSIDERED/REJECTED/SELECTED/BASED_ON edges. Query: provenance/create_decision."""
    raise NotImplementedError("TODO(siddharth): create_decision")


def decision_trace(graph: Graph, decision_id: str) -> list[Row]:
    """Full provenance trace of a Decision. Query: provenance/decision_trace."""
    raise NotImplementedError("TODO(siddharth): decision_trace")
