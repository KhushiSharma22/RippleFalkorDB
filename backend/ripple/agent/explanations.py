"""Explanation text built ONLY from recorded Decision trace rows and validator outcomes."""

from typing import Any


def explain(trace_rows: list[dict[str, Any]]) -> str:
    """Format a decision trace (from repository.decision_trace) as text. No invented facts."""
    raise NotImplementedError("TODO(siddharth): explanations")
