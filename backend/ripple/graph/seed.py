"""Builds the facility graph from a scenario YAML (simulator/scenarios/*.yaml).

Seeds only the scenario's `graph:` section, i.e. what the robot is allowed to *know*:
topology, capacities, services, locations, actions/conditions. The `truth:` section is
never read here; hidden truth stays in simulator.ground_truth (invariant #2).

Labels and relationship types can't be Cypher parameters, so the two seed templates take
`{labels}` / `{type}` placeholders filled ONLY from the whitelists below (D-010).
"""

from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml
from falkordb import Graph
from redis.exceptions import ResponseError

from ripple.graph.query_loader import load_query
from ripple.graph.schema import ensure_schema

# Allowed label sets and relationship types: mirrors docs/graph-model.md v1.
NODE_LABELS: set[tuple[str, ...]] = {
    ("Location",),
    ("Asset", "Supply"),
    ("Asset", "Valve"),
    ("Asset", "Header"),
    ("Asset", "Machine"),
    ("Service",),
    ("InspectionPoint",),
    ("Sensor",),
    ("Robot",),
    ("Action",),
    ("Condition",),
}
REL_TYPES: set[str] = {
    "ADJACENT_TO",
    "AT",
    "FEEDS",
    "CONNECTED_TO",
    "LOCATED_IN",
    "PROVIDES_SERVICE",
    "INSPECTS",
    "MEASURES",
    "REQUIRES",
    "CONDITION_ON",
    "AFFECTS",
}


def seed_from_scenario(graph: Graph, scenario_path: Path) -> dict[str, int]:
    """Clear `graph`, create schema, then batch-create the scenario's nodes and relationships.

    Returns {"nodes": n, "relationships": m} as reported by FalkorDB.
    Raises ValueError for a label set or relationship type outside the whitelist.
    """
    spec = yaml.safe_load(Path(scenario_path).read_text())["graph"]

    try:
        graph.delete()
    except ResponseError as e:
        if "empty key" not in str(e):
            raise
    ensure_schema(graph)

    nodes_by_labels: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for node in spec["nodes"]:
        labels = tuple(node["labels"])
        if labels not in NODE_LABELS:
            raise ValueError(f"Node {node.get('id')!r} has labels {labels} not in graph model")
        nodes_by_labels[labels].append({k: v for k, v in node.items() if k != "labels"})

    n_nodes = 0
    node_template = load_query("seed/create_nodes")
    for labels, rows in nodes_by_labels.items():
        query = node_template.replace("{labels}", ":".join(labels))
        n_nodes += int(graph.query(query, {"rows": rows}).nodes_created)

    rels_by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rel in spec["relationships"]:
        rel_type = rel["type"]
        if rel_type not in REL_TYPES:
            raise ValueError(
                f"Relationship {rel['from']}->{rel['to']} has type {rel_type!r} not in graph model"
            )
        props = {k: v for k, v in rel.items() if k not in ("type", "from", "to")}
        rels_by_type[rel_type].append({"from": rel["from"], "to": rel["to"], "props": props})

    n_rels = 0
    rel_template = load_query("seed/create_relationships")
    for rel_type, rows in rels_by_type.items():
        query = rel_template.replace("{type}", rel_type)
        n_rels += int(graph.query(query, {"rows": rows}).relationships_created)

    return {"nodes": n_nodes, "relationships": n_rels}
