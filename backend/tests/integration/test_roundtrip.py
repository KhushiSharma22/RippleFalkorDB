import pytest

@pytest.mark.integration
def test_asset_round_trip(graph):

    graph.query(
        "CREATE (:Asset:Supply {id: $id, capacity: $capacity})",
        {"id": "primary_supply", "capacity": 8},
    )


    rows = graph.ro_query(
        "MATCH (a:Asset {id: $id}) RETURN a.id, a.capacity, labels(a)",
        {"id": "primary_supply"},
    ).result_set

    assert len(rows) == 1
    asset_id, capacity, labels = rows[0]
    assert asset_id == "primary_supply"
    assert capacity == 8    
    assert set(labels) == {"Asset", "Supply"}