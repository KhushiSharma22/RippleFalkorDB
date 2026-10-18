from pathlib import Path

import pytest

from ripple.graph.seed import seed_from_scenario

SCENARIOS = Path(__file__).resolve().parents[2] / "ripple" / "simulator" / "scenarios"
EXPECTED = {"nodes": 27, "relationships": 49, "observations": 1}


@pytest.mark.integration
def test_seed_healthy_8(graph):
    assert seed_from_scenario(graph, SCENARIOS / "healthy_8.yaml") == EXPECTED

    machines = graph.ro_query(
        "MATCH (:Asset {id: $id})-[:FEEDS*1..]->(m:Machine) RETURN DISTINCT m.id",
        {"id": "primary_supply"},
    ).result_set
    assert {row[0] for row in machines} == {"machine_a", "machine_b"}

    at = graph.ro_query("MATCH (:Robot {id: 'robot_1'})-[:AT]->(l:Location) RETURN l.id").result_set
    assert at == [["dock"]]

    # Edge properties survive seeding.
    cost = graph.ro_query(
        "MATCH (:Location {id: 'dock'})-[e:ADJACENT_TO]->(:Location {id: 'standby_bay'}) RETURN e.cost"
    ).result_set
    assert cost == [[10]]

    # Re-seeding clears first and tolerates existing indexes.
    assert seed_from_scenario(graph, SCENARIOS / "healthy_8.yaml") == EXPECTED


@pytest.mark.integration
def test_seed_does_not_leak_truth(graph):
    seed_from_scenario(graph, SCENARIOS / "healthy_8.yaml")
    rows = graph.ro_query(
        "MATCH (n) WHERE n.health IS NOT NULL OR n.capacity IS NOT NULL OR n.position IS NOT NULL "
        "RETURN n.id"
    ).result_set
    assert rows == []


@pytest.mark.integration
def test_seed_rejects_unknown_label(graph, tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("graph:\n  nodes:\n    - {labels: [Bogus], id: x}\n  relationships: []\n")
    with pytest.raises(ValueError, match="Bogus"):
        seed_from_scenario(graph, bad)


@pytest.mark.integration
def test_seed_rejects_unknown_relationship_type(graph, tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "graph:\n  nodes:\n    - {labels: [Location], id: a}\n    - {labels: [Location], id: b}\n"
        "  relationships:\n    - {type: TELEPORTS_TO, from: a, to: b}\n"
    )
    with pytest.raises(ValueError, match="TELEPORTS_TO"):
        seed_from_scenario(graph, bad)
