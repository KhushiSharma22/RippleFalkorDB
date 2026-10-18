import pytest

from ripple.evidence.freshness import freshness_window, is_fresh
from ripple.planning.validator import compare
from ripple.scenario import SCENARIOS_DIR, load_scenario
from ripple.simulator import controls, facility
from ripple.simulator.ground_truth import GroundTruth


def test_freshness_windows_differ_by_property() -> None:
    assert freshness_window("position") < freshness_window("health")
    assert is_fresh("position", observed_at=100.0, now=200.0)
    assert not is_fresh("position", observed_at=0.0, now=1000.0)


def test_compare_ops() -> None:
    assert compare("=", "ok", "ok")
    assert not compare("=", "failed", "ok")
    assert compare("=", 8, 8.0)
    assert compare(">=", 8, 7)
    with pytest.raises(ValueError):
        compare("~", 1, 1)


def test_scenario_extends_merges_truth_and_inherits_graph() -> None:
    base = load_scenario(SCENARIOS_DIR / "healthy_8.yaml")
    down = load_scenario(SCENARIOS_DIR / "standby_down.yaml")
    assert down["graph"] == base["graph"]
    assert down["truth"]["standby_supply"]["health"] == "failed"
    assert down["truth"]["standby_supply"]["running"] is False  # inherited key kept


def test_header_flow_requires_healthy_running_supply_and_open_valve() -> None:
    truth = GroundTruth.from_scenario(SCENARIOS_DIR / "healthy_8.yaml")
    assert facility.header_flow(truth, "cooling_header") == 0.0  # primary failed, standby off
    controls.apply_effect(truth, "standby_supply", "running", True, now=1.0)
    assert facility.header_flow(truth, "cooling_header") == 0.0  # bypass still closed
    controls.apply_effect(truth, "bypass", "position", "open", now=2.0)
    assert facility.header_flow(truth, "cooling_header") == 8.0


def test_ack_is_not_effect() -> None:
    truth = GroundTruth(
        {"bypass": {"position": "closed", "stuck": True}, "pump": {"health": "failed"}}
    )
    assert controls.apply_effect(truth, "bypass", "position", "open", now=1.0)["accepted"]
    assert truth.get("bypass", "position") == "closed"
    assert controls.apply_effect(truth, "pump", "running", True, now=1.0)["accepted"]
    assert truth.get("pump", "running") is None
