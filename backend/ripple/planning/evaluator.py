"""Ranks validated plans by service preservation, time, and inspection effort."""

from typing import Any


def rank_plans(evaluations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Order plan evaluations best-first. Hard constraints already applied by validator."""
    raise NotImplementedError("TODO(siddharth): plan ranking")
