"""Builds Decision records (considered/rejected/selected plans, evidence used, revision)."""

from typing import Any


def record_decision(incident_id: str, evaluations: list[dict[str, Any]], selected_plan_id: str) -> str:
    """Assemble and persist a Decision via repository.create_decision; return its id."""
    raise NotImplementedError("TODO(siddharth): record decision")
