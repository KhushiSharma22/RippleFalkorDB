"""Simulated facility physics, deliberately simple (no hydraulics).

Header flow = sum of supply capacity over the header's `flow_paths` (in the hidden truth) whose
supply is healthy and running and whose valve is open. Temperature dynamics and time-stepping
arrive in later milestones.
"""

from typing import Any

from ripple.simulator.ground_truth import GroundTruth


def header_flow(truth: GroundTruth, header_id: str) -> float:
    total = 0.0
    for supply_id, valve_id in truth.get(header_id, "flow_paths", []):
        supplying = truth.get(supply_id, "health") == "ok" and truth.get(
            supply_id, "running", False
        )
        if supplying and truth.get(valve_id, "position") == "open":
            total += float(truth.get(supply_id, "capacity", 0))
    return total


def observe(truth: GroundTruth, asset_id: str, prop: str) -> Any:
    """True value of an asset property as a perfect sensor would read it (None if unknown)."""
    if prop == "flow":
        return header_flow(truth, asset_id)
    return truth.get(asset_id, prop)
