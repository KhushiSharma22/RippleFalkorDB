"""Milestone 2: multi-hop impact; the obvious local fix is rejected for downstream critical impact."""

import pytest

from ripple.graph import repository
from ripple.graph.seed import seed_from_scenario
from ripple.planning import capacity
from ripple.planning.validator import validate_plan
from ripple.scenario import SCENARIOS_DIR

pytestmark = [pytest.mark.integration, pytest.mark.scenario]


def test_multi_hop_impact_queries(graph):
    seed_from_scenario(graph, SCENARIOS_DIR / "healthy_8.yaml")
    downstream = {
        r["asset_id"]: r["hops"] for r in repository.affected_assets(graph, "primary_supply")
    }
    assert downstream == {"main_isolation": 1, "cooling_header": 2, "machine_a": 3, "machine_b": 3}
    assert [
        s["service_id"] for s in repository.critical_services_affected(graph, "primary_supply")
    ] == ["line_a"]
    alternates = repository.alternate_supplies(graph, "machine_a", "primary_supply")
    assert alternates == [
        {"supply_id": "standby_supply", "nominal_capacity": 8, "valves_on_path": ["bypass"]}
    ]


def test_incident_traces_shared_dependency(make_world):
    result = make_world("healthy_8")[0].run_incident("machine_a")
    assert result.impact["shared_with"] == ["machine_b"]
    assert result.impact["critical_services"] == ["line_a"]
    assert result.impact["header"] == "cooling_header"


def test_isolating_primary_now_is_rejected_for_critical_impact(make_world):
    result = make_world("healthy_8")[0].run_incident("machine_a")
    reasons = result.rejected["isolate_primary_now"]
    assert any("available 0 < demand 7" in r and "line_a (machine_a)" in r for r in reasons)
    assert result.chosen_plan == "restore_via_standby"


def test_insufficient_standby_forces_load_reduction(make_world):
    orchestrator, truth, _ = make_world("healthy_5")
    result = orchestrator.run_incident("machine_a")

    assert any("available 5 < demand 7" in r for r in result.rejected["restore_via_standby"])
    assert result.chosen_plan == "reduce_load_then_restore"
    assert result.recovered
    assert result.service == {"header": "cooling_header", "flow": 5.0, "required": 4.0}


def test_capacity_needs_no_inspection_when_answer_is_already_decided(graph):
    """Decision-driven: with no evidence at all, isolating primary has at most 8 >= 7, so evidence is
    requested; once the robot sees standby isn't running, the shortfall is certain."""
    seed_from_scenario(graph, SCENARIOS_DIR / "healthy_8.yaml")
    undecided = capacity.demand_within_capacity(graph, "cooling_header", 1000.0, "isolate_primary")
    assert not undecided.ok and undecided.missing and not undecided.violations

    plan = validate_plan(graph, ["activate_standby", "open_bypass", "isolate_primary"], 1000.0)
    assert ("standby_supply", "health") in plan.missing
    assert not plan.rejected  # predicted effects of earlier steps satisfy later prerequisites
