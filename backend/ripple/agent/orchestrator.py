"""The core loop: observe -> update evidence -> query dependencies -> identify uncertainty ->
inspect -> evaluate plans -> validate -> execute -> verify (-> replan on failure).

Milestone 1 (vertical slice): candidate plans are a fixed, ordered list; everything else comes
from the graph: prerequisites, where to inspect, robot location, declared effects. Sensing and
actuation are injected callables, so this module never touches the simulator's hidden truth
(invariant #2). Graph-driven candidates, impact analysis and branch evaluation replace the fixed
list in Milestones 2-4.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from falkordb import Graph

from ripple.evidence.models import Observation
from ripple.graph import repository
from ripple.planning.validator import ValidationResult, check_action, compare
from ripple.robot.base import Pose, RobotAdapter, arrived

# Preference order: restore full service first, degrade only if that is infeasible.
CANDIDATE_PLANS: dict[str, list[str]] = {
    "restore_via_standby": ["activate_standby", "open_bypass"],
    "shed_noncritical_load": ["shed_load_b"],
}
MAX_INSPECTION_ROUNDS = 3
MOVE_RETRIES = 2

Sense = Callable[[str], list[Observation]]  # inspection_point_id -> observations
Actuate = Callable[[str, str, Any], dict[str, Any]]  # (asset_id, property, value) -> ack


class RobotMoveFailed(Exception):
    """The robot did not verifiably arrive after retries."""


@dataclass
class IncidentResult:
    incident_id: str
    chosen_plan: str | None
    rejected: dict[str, list[str]] = field(default_factory=dict)  # plan -> reasons
    inspections: list[str] = field(default_factory=list)  # inspection point ids, in order
    attempts: list[dict[str, Any]] = field(default_factory=list)
    recovered: bool = False


class Orchestrator:
    def __init__(
        self,
        graph: Graph,
        robot: RobotAdapter,
        sense: Sense,
        actuate: Actuate,
        clock: Callable[[], float],
        robot_id: str = "robot_1",
    ) -> None:
        self.graph = graph
        self.robot = robot
        self.sense = sense
        self.actuate = actuate
        self.clock = clock
        self.robot_id = robot_id

    def run_incident(self, trigger_asset_id: str) -> IncidentResult:
        """Handle an alarm on `trigger_asset_id`; return what was chosen, rejected, inspected, verified."""
        incident_id = f"inc_{uuid4().hex[:8]}"
        repository.open_incident(self.graph, incident_id, trigger_asset_id, self.clock())
        result = IncidentResult(incident_id=incident_id, chosen_plan=None)

        for name, plan in CANDIDATE_PLANS.items():
            check = self._gather_evidence_and_check(plan[0], result)
            if not check.ok:
                result.rejected[name] = check.reasons
                continue
            result.chosen_plan = name
            result.recovered = self._execute(plan, result)
            return result
        return result

    # --- evidence ---------------------------------------------------------------
    def _gather_evidence_and_check(
        self, action_id: str, result: IncidentResult
    ) -> ValidationResult:
        """Validate an action; inspect any missing/stale evidence it depends on, then re-validate."""
        check = check_action(self.graph, action_id, self.clock())
        for _ in range(MAX_INSPECTION_ROUNDS):
            if check.ok or not check.missing:
                return check
            for asset_id, prop in check.missing:
                self._inspect(asset_id, prop, result)
            check = check_action(self.graph, action_id, self.clock())
        return check

    def _inspect(self, asset_id: str, prop: str, result: IncidentResult) -> list[Observation]:
        """Send the robot to an inspection point covering asset.prop, sense, and record evidence."""
        points = repository.inspection_points_for(self.graph, asset_id, prop)
        if not points:
            return []
        ip = points[0]
        self._go_to(ip["location_id"], Pose(ip["x"], ip["y"]))
        observations = self.sense(ip["ip_id"])
        for obs in observations:
            obs.incident_id = result.incident_id
            repository.insert_observation(self.graph, obs)
        result.inspections.append(ip["ip_id"])
        return observations

    def _go_to(self, location_id: str, pose: Pose) -> None:
        """Command a move; update the graph's AT edge only after verified arrival (DP4)."""
        here = repository.robot_location(self.graph, self.robot_id)
        if here is not None and here["location_id"] == location_id:
            return
        for _ in range(MOVE_RETRIES):
            self.robot.move_to(pose)
            if arrived(self.robot.current_pose(), pose):
                repository.set_robot_location(self.graph, self.robot_id, location_id, self.clock())
                return
        raise RobotMoveFailed(f"{self.robot_id} did not reach {location_id}")

    # --- execution --------------------------------------------------------------
    def _execute(self, plan: list[str], result: IncidentResult) -> bool:
        """Run each action: recheck prerequisites, send, record ack, verify by observation."""
        for action_id in plan:
            recheck = check_action(self.graph, action_id, self.clock())
            if not recheck.ok:
                result.attempts.append(
                    {"action": action_id, "status": "rejected", "reasons": recheck.reasons}
                )
                return False
            for effect in repository.action_effects(self.graph, action_id):
                if not self._attempt(action_id, effect, result):
                    return False
        return True

    def _attempt(self, action_id: str, effect: dict[str, Any], result: IncidentResult) -> bool:
        asset_id, prop, expected = effect["asset_id"], effect["property"], effect["value"]
        attempt_id = f"att_{uuid4().hex[:8]}"
        repository.create_attempt(
            self.graph,
            attempt_id,
            action_id,
            result.incident_id,
            asset_id,
            prop,
            expected,
            self.clock(),
        )
        ack = self.actuate(asset_id, prop, expected)
        repository.update_attempt(
            self.graph, attempt_id, "acked" if ack["accepted"] else "rejected", ack["acked_at"]
        )

        observed = [
            o
            for o in self._inspect(asset_id, prop, result)
            if o.asset_id == asset_id and o.property == prop
        ]
        status = "unverified"
        if observed:
            status = "verified" if compare("=", observed[0].value, expected) else "failed"
            repository.verify_attempt(self.graph, attempt_id, observed[0].id, status)
        result.attempts.append(
            {
                "action": action_id,
                "asset": asset_id,
                "property": prop,
                "expected": expected,
                "status": status,
            }
        )
        return status == "verified"
