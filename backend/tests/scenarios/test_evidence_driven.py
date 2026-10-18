"""Milestone 3: freshness, hypotheses, decision relevance score, inspection selection, routing."""

import pytest

from ripple.graph import repository
from ripple.graph.seed import seed_from_scenario
from ripple.planning.validator import check_action
from ripple.scenario import SCENARIOS_DIR

pytestmark = [pytest.mark.integration, pytest.mark.scenario]


def test_robot_only_travels_for_decision_relevant_inspections(make_world):
    result = make_world("healthy_8")[0].run_incident("machine_a")
    diagnosis = result.inspected("diagnosis")
    assert set(diagnosis) == {"ip_primary_pump", "ip_standby_pump"}
    # The main valve only distinguishes hypotheses; it can't change the plan, so no diagnostic trip.
    first_round = {c["ip_id"]: c for c in result.rankings[0]}
    assert first_round["ip_main_valve"]["blocks"] == []
    assert "ip_main_valve" not in diagnosis


def test_decision_relevance_score_prefers_plan_blocking_evidence(make_world):
    result = make_world("healthy_8")[0].run_incident("machine_a")
    ranking = result.rankings[0]
    assert [c["score"] for c in ranking] == sorted((c["score"] for c in ranking), reverse=True)
    top = ranking[0]
    assert top["ip_id"] in {"ip_primary_pump", "ip_standby_pump"}
    assert len(top["blocks"]) == 3 and top["critical"] == 1


def test_stale_log_is_not_trusted(graph, make_world):
    orchestrator, _, _ = make_world("stale_valve")
    check = check_action(graph, "isolate_primary", 1000.0)
    assert ("bypass", "position") in check.missing  # hour-old "open" log is stale, not evidence
    assert any("stale (log)" in n for n in check.notes)

    result = orchestrator.run_incident("machine_a")
    stale = {(s["asset_id"], s["property"]): s["last_seen"] for s in result.stale_at_start}
    assert stale[("bypass", "position")] == -3600.0
    assert result.recovered


def test_hypotheses_get_evidence_links(graph, make_world):
    result = make_world("healthy_8")[0].run_incident("machine_a")
    open_h = {h["hypothesis_id"].split(":")[1]: h for h in result.hypotheses}
    assert open_h["hyp_primary_failure"]["supporting"] == 1
    assert "hyp_faulty_temperature" not in open_h  # contradicted by primary health = failed
    rows = graph.ro_query(
        "MATCH (:Observation)-[r:CONTRADICTS]->(h:Hypothesis) RETURN h.template, r.rule"
    ).result_set
    assert ["hyp_faulty_temperature", "primary_supply.health = 'ok'"] in rows


def test_route_uses_adjacency_costs_hop_by_hop(graph):
    seed_from_scenario(graph, SCENARIOS_DIR / "healthy_8.yaml")
    route = repository.route_to_inspection_point(graph, "robot_1", "ip_header_flow")
    assert route["locations"] == ["dock", "primary_bay", "header_room"] or route["locations"] == [
        "dock",
        "standby_bay",
        "header_room",
    ]
    assert route["cost"] == 18.0
    repository.set_robot_location(graph, "robot_1", "standby_bay", 1.0)
    assert repository.route_to_inspection_point(graph, "robot_1", "ip_bypass_valve")["cost"] == 0.0


def test_robot_ends_where_its_last_verified_hop_was(graph, make_world):
    result = make_world("healthy_8")[0].run_incident("machine_a")
    assert result.inspected()[-1] == "ip_header_flow"
    assert repository.robot_location(graph, "robot_1")["location_id"] == "header_room"
    assert result.travel_cost > 0
