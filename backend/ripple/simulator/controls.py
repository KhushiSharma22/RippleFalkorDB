"""Simulated equipment commands: attempt -> ack -> (maybe) state change.

An ack is a receipt, not proof the state changed."""

from typing import Any

from ripple.simulator.ground_truth import GroundTruth


def send_command(truth: GroundTruth, asset_id: str, command: str) -> dict[str, Any]:
    """Apply a command (subject to faults like stuck valves) and return an ack receipt."""
    raise NotImplementedError("TODO(siddharth): simulated controls")
