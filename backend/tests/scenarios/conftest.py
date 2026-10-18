"""Shared world builder for end-to-end scenario tests (FalkorDB required)."""

import pytest

from ripple.agent.orchestrator import Orchestrator
from ripple.graph.seed import seed_from_scenario
from ripple.robot.base import Pose
from ripple.robot.mock_adapter import MockRobotAdapter
from ripple.scenario import SCENARIOS_DIR
from ripple.simulator import controls, sensors
from ripple.simulator.ground_truth import GroundTruth


class FakeClock:
    def __init__(self, start: float = 1000.0) -> None:
        self.t = start

    def __call__(self) -> float:
        self.t += 1.0
        return self.t


@pytest.fixture
def make_world(graph):
    """make_world(scenario) -> (orchestrator, truth, robot), wired to a freshly seeded graph."""

    def build(scenario: str):
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

    return build
