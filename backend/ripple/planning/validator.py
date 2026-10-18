"""Hard-constraint checks: prerequisites, evidence freshness, state-revision consistency.

Deterministic; has final say over the LLM. Prerequisites come from the graph
(actions/action_prerequisites); current beliefs come from the latest Observation per
(asset, property), and only fresh ones count.
"""

from dataclasses import dataclass, field
from typing import Any

from falkordb import Graph

from ripple.evidence.freshness import is_fresh
from ripple.graph import repository


@dataclass
class ValidationResult:
    ok: bool
    reasons: list[str] = field(default_factory=list)
    missing: list[tuple[str, str]] = field(default_factory=list)  # (asset_id, property) to inspect


def compare(op: str, observed: Any, expected: Any) -> bool:
    """Evaluate `observed <op> expected`; numeric ops coerce to float."""
    if op == "=":
        if isinstance(observed, (int, float)) and isinstance(expected, (int, float)):
            return float(observed) == float(expected)
        return observed == expected
    numeric = {"<": float.__lt__, "<=": float.__le__, ">": float.__gt__, ">=": float.__ge__}
    if op not in numeric:
        raise ValueError(f"Unsupported condition op {op!r}")
    return numeric[op](float(observed), float(expected))


def check_action(graph: Graph, action_id: str, now: float) -> ValidationResult:
    """Check every prerequisite of `action_id` against fresh evidence.

    Missing or stale evidence is reported in `missing` (so the robot can inspect it);
    a fresh observation that violates a condition is a hard rejection.
    """
    reasons: list[str] = []
    missing: list[tuple[str, str]] = []
    for c in repository.action_prerequisites(graph, action_id):
        if c["kind"] == "computed":
            reasons.append(
                f"{c['condition_id']}: computed check {c['check']!r} not implemented (Milestone 2)"
            )
            continue
        latest = repository.latest_observation(graph, c["asset_id"], c["property"])
        target = f"{c['asset_id']}.{c['property']}"
        if latest is None:
            missing.append((c["asset_id"], c["property"]))
            reasons.append(f"{c['condition_id']}: no evidence for {target}")
        elif not is_fresh(c["property"], latest["observed_at"], now):
            missing.append((c["asset_id"], c["property"]))
            reasons.append(
                f"{c['condition_id']}: evidence for {target} is stale ({latest['source']})"
            )
        elif not compare(c["op"], latest["value"], c["value"]):
            reasons.append(
                f"{c['condition_id']}: {target} = {latest['value']!r}, required {c['op']} {c['value']!r}"
            )
    return ValidationResult(ok=not reasons, reasons=reasons, missing=missing)


def validate_plan(graph: Graph, plan: list[Any], now: float) -> ValidationResult:
    """Reject plans violating prerequisites or relying on stale evidence (Milestone 3/4)."""
    raise NotImplementedError("TODO(siddharth): plan validation")


def recheck_before_action(graph: Graph, step: Any, expected_revision: int) -> ValidationResult:
    """Re-validate a step against the latest StateRevision immediately before executing (Milestone 3)."""
    raise NotImplementedError("TODO(siddharth): pre-action recheck")
