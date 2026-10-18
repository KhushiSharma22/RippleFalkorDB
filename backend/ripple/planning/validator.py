"""Hard-constraint checks: prerequisites, evidence freshness, capacity.

Deterministic; has final say over the LLM. Prerequisites come from the graph
(actions/action_prerequisites); beliefs come from the latest fresh Observation per
(asset, property), or from a planning prediction for effects of earlier plan steps.

Outcome per action/plan:
- violations: fresh (or predicted) facts break a condition -> hard reject
- missing:    evidence absent or stale -> the robot could inspect it
"""

from dataclasses import dataclass, field

from falkordb import Graph

from ripple.evidence.beliefs import Predicted, belief, compare
from ripple.graph import repository
from ripple.planning import capacity
from ripple.planning.transition_model import with_effects


@dataclass
class ValidationResult:
    violations: list[str] = field(default_factory=list)
    missing: list[tuple[str, str]] = field(default_factory=list)  # (asset_id, property)
    notes: list[str] = field(default_factory=list)  # why each missing item is needed

    @property
    def ok(self) -> bool:
        return not self.violations and not self.missing

    @property
    def rejected(self) -> bool:
        return bool(self.violations)

    @property
    def reasons(self) -> list[str]:
        return self.violations + self.notes

    def merge(self, other: "ValidationResult", prefix: str = "") -> None:
        self.violations += [prefix + v for v in other.violations]
        self.notes += [prefix + n for n in other.notes]
        self.missing += [m for m in other.missing if m not in self.missing]


def check_action(
    graph: Graph, action_id: str, now: float, predicted: Predicted | None = None
) -> ValidationResult:
    """Check every prerequisite of `action_id` against fresh evidence (+ optional predictions)."""
    result = ValidationResult()
    for c in repository.action_prerequisites(graph, action_id):
        cid, asset_id = c["condition_id"], c["asset_id"]
        if c["kind"] == "computed":
            if c["check"] != "demand_within_capacity":
                result.violations.append(f"{cid}: unknown computed check {c['check']!r}")
                continue
            cap = capacity.demand_within_capacity(graph, asset_id, now, action_id, predicted)
            result.violations += [f"{cid}: {v}" for v in cap.violations]
            for item in cap.missing:
                if item not in result.missing:
                    result.missing.append(item)
            if cap.missing:
                result.notes.append(f"{cid}: capacity undetermined, need {cap.missing}")
            continue

        b = belief(graph, asset_id, c["property"], now, predicted)
        target = f"{asset_id}.{c['property']}"
        if b.usable:
            if not compare(c["op"], b.value, c["value"]):
                result.violations.append(
                    f"{cid}: {target} = {b.value!r} ({b.status}), required {c['op']} {c['value']!r}"
                )
        else:
            if (asset_id, c["property"]) not in result.missing:
                result.missing.append((asset_id, c["property"]))
            why = "no evidence" if b.status == "missing" else f"evidence is stale ({b.source})"
            result.notes.append(f"{cid}: {why} for {target}")
    return result


def validate_plan(graph: Graph, actions: list[str], now: float) -> ValidationResult:
    """Validate a sequence: each step sees the predicted effects of the steps before it."""
    result = ValidationResult()
    predicted: Predicted = {}
    for action_id in actions:
        result.merge(check_action(graph, action_id, now, predicted), prefix=f"{action_id} -> ")
        predicted = with_effects(graph, action_id, predicted)
    return result


def recheck_before_action(graph: Graph, action_id: str, now: float) -> ValidationResult:
    """Re-validate one action against real evidence only, right before executing it (invariant #4)."""
    return check_action(graph, action_id, now)
