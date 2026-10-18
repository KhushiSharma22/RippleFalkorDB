"""HIDDEN true facility state. Never imported by agent/, planning/, or evidence/.

Enforced by tests/test_architecture.py. Only the simulator (facility, controls, sensors) reads
or writes it; Ripple learns about it only through location-gated sensor Observations.
"""

from pathlib import Path
from typing import Any

from ripple.scenario import load_scenario


class GroundTruth:
    """True per-asset state, e.g. {"standby_supply": {"health": "ok", "capacity": 8}}."""

    def __init__(self, state: dict[str, dict[str, Any]]) -> None:
        self._state = {asset: dict(props) for asset, props in state.items()}

    @classmethod
    def from_scenario(cls, scenario_path: Path | str) -> "GroundTruth":
        return cls(load_scenario(scenario_path).get("truth", {}))

    def get(self, asset_id: str, prop: str, default: Any = None) -> Any:
        return self._state.get(asset_id, {}).get(prop, default)

    def set(self, asset_id: str, prop: str, value: Any) -> None:
        self._state.setdefault(asset_id, {})[prop] = value
