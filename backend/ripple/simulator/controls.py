"""Simulated equipment commands: attempt -> ack -> (maybe) state change.

An ack is a receipt, not proof the state changed (invariant #3). Commands are accepted but
have no effect when the equipment is `stuck`, or when starting equipment whose health is not ok.
"""

from typing import Any

from ripple.simulator.ground_truth import GroundTruth


def apply_effect(
    truth: GroundTruth, asset_id: str, prop: str, value: Any, now: float
) -> dict[str, Any]:
    """Attempt to set `asset_id.prop = value`; always returns an ack receipt."""
    stuck = truth.get(asset_id, "stuck", False)
    cannot_start = (
        prop == "running" and value is True and truth.get(asset_id, "health", "ok") != "ok"
    )
    if not (stuck or cannot_start):
        truth.set(asset_id, prop, value)
    return {"accepted": True, "acked_at": now}
