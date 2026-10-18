"""Scenario file loading (shared by graph seeding and the simulator).

A scenario YAML has `graph:` (what Ripple may know; seeded into FalkorDB) and `truth:`
(hidden; read only by the simulator). `extends: <name>` reuses another scenario in the
same directory: `graph` is inherited unless redefined, and `truth` is merged per asset.
"""

from pathlib import Path
from typing import Any

import yaml

SCENARIOS_DIR = Path(__file__).parent / "simulator" / "scenarios"


def load_scenario(path: Path | str) -> dict[str, Any]:
    path = Path(path)
    spec = yaml.safe_load(path.read_text())
    parent_name = spec.get("extends")
    if not parent_name:
        return spec
    parent = load_scenario(path.parent / f"{parent_name}.yaml")
    truth = {asset: dict(props) for asset, props in parent.get("truth", {}).items()}
    for asset, props in spec.get("truth", {}).items():
        truth.setdefault(asset, {}).update(props)
    return {**parent, **spec, "graph": spec.get("graph", parent["graph"]), "truth": truth}
