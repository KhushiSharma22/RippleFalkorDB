"""Builds the facility graph from a scenario YAML (simulator/scenarios/*.yaml).

Seeds only what the robot is allowed to *know*: topology, capacities, services, locations,
actions/conditions, prior observations. Hidden truth stays in simulator.ground_truth."""

from pathlib import Path

from falkordb import Graph


def seed_from_scenario(graph: Graph, scenario_path: Path) -> None:
    """Clear `graph` and create nodes/relationships described by the scenario file."""
    raise NotImplementedError("TODO(siddharth): seed graph from scenario")
