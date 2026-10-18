"""Milestone 1 vertical slice: the robot's observation changes the chosen action.

Same code, same graph topology; only the hidden truth differs between scenarios.
"""

import pytest

from ripple.agent.orchestrator import Orchestrator, RobotMoveFailed
from ripple.graph import repository
from ripple.graph.seed import seed_from_scenario
from ripple.robot.base import Pose
from ripple.robot.mock_adapter import MockRobotAdapter
from ripple.scenario import SCENARIOS_DIR
from ripple.simulator import controls, facility, sensors
from ripple.simulator.ground_truth import GroundTruth

pytestmark = [pytest.mark.integration, pytest.mark.scenario]


class FakeClock:
    def __init__(self, start: float = 1000.0) -> None:
        self.t = start

    def __call__(self) -> float:
        self.t += 1.0
        return self.t


def make_world(graph, scenario: str):
    path = SCENARIOS_DIR / f"{scenario}.yaml"
    seed_from_scenario(graph, path)
    truth = GroundTruth.from_scenario(path)
    clock = FakeClock()
    robot = MockRobotAdapter(start=Pose(0.0, 0.0))
    orchestrator = Orchestrator(
        graph,
        robot,
        sense=lambda ip: sensors.read(graph, truth, "robot_1", ip, clock()),
        actuate=lambda asset, prop, value: controls.apply_effect(
            truth, asset, prop, value, clock()
        ),
        clock=clock,
    )
    return orchestrator, truth, robot


def test_healthy_standby_restores_service(graph):
    orchestrator, truth, _ = make_world(graph, "healthy_8")
    result = orchestrator.run_incident("machine_a")

    assert result.chosen_plan == "restore_via_standby"
    assert result.recovered
    # No standby health evidence exists (only a day-old capacity log), so the robot inspects first.
    assert result.inspections[0] == "ip_standby_pump"
    assert [a["status"] for a in result.attempts] == ["verified", "verified"]
    assert facility.header_flow(truth, "cooling_header") == 8.0
    assert repository.robot_location(graph, "robot_1")["location_id"] == "standby_bay"


def test_failed_standby_changes_the_chosen_action(graph):
    orchestrator, truth, _ = make_world(graph, "standby_down")
    result = orchestrator.run_incident("machine_a")

    assert "restore_via_standby" in result.rejected
    assert any("'failed'" in r for r in result.rejected["restore_via_standby"])
    assert result.chosen_plan == "shed_noncritical_load"
    assert result.recovered
    assert truth.get("machine_b", "running") is False


def test_observation_is_what_changes_the_decision(graph):
    healthy = make_world(graph, "healthy_8")[0].run_incident("machine_a").chosen_plan
    down = make_world(graph, "standby_down")[0].run_incident("machine_a").chosen_plan
    assert healthy != down


def test_stuck_valve_is_caught_by_verification_not_by_ack(graph):
    orchestrator, truth, _ = make_world(graph, "healthy_8")
    truth.set("bypass", "stuck", True)
    result = orchestrator.run_incident("machine_a")

    assert result.chosen_plan == "restore_via_standby"
    assert not result.recovered
    assert result.attempts[-1]["action"] == "open_bypass"
    assert result.attempts[-1]["status"] == "failed"  # acked, but observation shows still closed


def test_sensor_refuses_reading_away_from_inspection_point(graph):
    path = SCENARIOS_DIR / "healthy_8.yaml"
    seed_from_scenario(graph, path)
    with pytest.raises(sensors.NotAtInspectionPoint):
        sensors.read(graph, GroundTruth.from_scenario(path), "robot_1", "ip_header_flow", 1.0)


def test_failed_move_is_not_trusted(graph):
    orchestrator, _, robot = make_world(graph, "healthy_8")
    robot.fail_next_moves(5)
    with pytest.raises(RobotMoveFailed):
        orchestrator.run_incident("machine_a")
    assert repository.robot_location(graph, "robot_1")["location_id"] == "dock"
