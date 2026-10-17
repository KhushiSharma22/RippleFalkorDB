"""Hard-constraint checks: prerequisites, evidence freshness, state-revision consistency.

Deterministic; has final say over the LLM."""

from dataclasses import dataclass, field
from typing import Any

from falkordb import Graph


@dataclass
class ValidationResult:
    ok: bool
    reasons: list[str] = field(default_factory=list)


def validate_plan(graph: Graph, plan: list[Any], now: float) -> ValidationResult:
    """Reject plans violating prerequisites or relying on stale evidence."""
    raise NotImplementedError("TODO(siddharth): plan validation")


def recheck_before_action(graph: Graph, step: Any, expected_revision: int) -> ValidationResult:
    """Re-validate a step against the latest StateRevision immediately before executing."""
    raise NotImplementedError("TODO(siddharth): pre-action recheck")
