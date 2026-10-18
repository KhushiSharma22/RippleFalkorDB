"""Milestone 1: the robot's observation changes the chosen action; acks are not success."""

import pytest

from ripple.agent.orchestrator import RobotMoveFailed
from ripple.graph import repository
from ripple.graph.seed import seed_from_scenario
from ripple.scenario import SCENARIOS_DIR
from ripple.simulator import facility, sensors
from ripple.simulator.ground_truth import GroundTruth

pytestmark = [pytest.mark.integration, pytest.mark.scenario]


def test_healthy_standby_restores_service(graph, make_world):
    orchestrator, truth, _ = make_world("healthy_8")
    result = orchestrator.run_incident("machine_a")

    assert result.chosen_plan == "restore_via_standby"
    assert result.recovered
    assert [a["action"] for a in result.attempts] == [
        "activate_standby",
        "open_bypass",
        "isolate_primary",
    ]
    assert all(a["status"] == "verified" for a in result.attempts)
    assert facility.header_flow(truth, "cooling_header") == 8.0
    assert result.service == {"header": "cooling_header", "flow": 8.0, "required": 7.0}


def test_observation_is_what_changes_the_decision(make_world):
    """Same code, same graph topology; only the hidden truth (and so the observations) differ."""
    chosen = {
        s: make_world(s)[0].run_incident("machine_a").chosen_plan
        for s in ("healthy_8", "healthy_5", "standby_down")
    }
    assert chosen == {
        "healthy_8": "restore_via_standby",
        "healthy_5": "reduce_load_then_restore",
        "standby_down": "shed_noncritical_load",
    }


def test_failed_standby_degrades_honestly(make_world):
    orchestrator, truth, _ = make_world("standby_down")
    result = orchestrator.run_incident("machine_a")

    assert result.chosen_plan == "shed_noncritical_load"
    assert any("'failed'" in r for r in result.rejected["restore_via_standby"])
    assert truth.get("machine_b", "running") is False
    assert not result.recovered  # machine A is still unserved: degraded, not "recovered"
    assert result.service["flow"] == 0.0


def test_stuck_valve_is_caught_by_verification_not_by_ack(make_world):
    orchestrator, _, _ = make_world("stuck_valve")
    result = orchestrator.run_incident("machine_a")

    assert result.chosen_plan == "restore_via_standby"
    assert not result.recovered
    assert result.attempts[-1] == {
        "action": "open_bypass",
        "asset": "bypass",
        "property": "position",
        "expected": "open",
        "status": "failed",  # acked, but the observation shows it still closed
    }


def test_sensor_refuses_reading_away_from_inspection_point(graph):
    path = SCENARIOS_DIR / "healthy_8.yaml"
    seed_from_scenario(graph, path)
    with pytest.raises(sensors.NotAtInspectionPoint):
        sensors.read(graph, GroundTruth.from_scenario(path), "robot_1", "ip_header_flow", 1.0)


def test_failed_move_is_not_trusted(graph, make_world):
    orchestrator, _, robot = make_world("healthy_8")
    robot.fail_next_moves(5)
    with pytest.raises(RobotMoveFailed):
        orchestrator.run_incident("machine_a")
    assert repository.robot_location(graph, "robot_1")["location_id"] == "dock"
