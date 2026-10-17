"""HIDDEN true facility state. Never imported by agent/, planning/, or evidence/.

Enforced by tests/test_architecture.py. Only sensors.py and controls.py read/write it."""

from pathlib import Path


class GroundTruth:
    """True state: supply health, valve positions, flows, temperatures, active faults."""

    @classmethod
    def from_scenario(cls, scenario_path: Path) -> "GroundTruth":
        raise NotImplementedError("TODO(siddharth): load hidden truth from scenario")
