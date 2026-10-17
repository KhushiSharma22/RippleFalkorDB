"""Structured tools exposed to the LLM (and MCP). Each wraps repository / planning calls."""

from typing import Any


def get_affected_assets(asset_id: str) -> list[dict[str, Any]]:
    raise NotImplementedError("TODO(siddharth): tool")


def get_missing_evidence(incident_id: str) -> list[dict[str, Any]]:
    raise NotImplementedError("TODO(siddharth): tool")


def rank_inspections(incident_id: str) -> list[dict[str, Any]]:
    raise NotImplementedError("TODO(siddharth): tool")


def evaluate_plans(incident_id: str) -> list[dict[str, Any]]:
    raise NotImplementedError("TODO(siddharth): tool")


def request_inspection(inspection_point_id: str) -> dict[str, Any]:
    raise NotImplementedError("TODO(siddharth): tool")


def execute_step(plan_id: str, step_index: int) -> dict[str, Any]:
    raise NotImplementedError("TODO(siddharth): tool")
