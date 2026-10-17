"""Per-property freshness windows: how long an observation of a property stays usable."""

from datetime import timedelta

from ripple.evidence.models import Observation


def freshness_window(prop: str) -> timedelta:
    """Window for `prop` (e.g. valve position vs. pump health)."""
    raise NotImplementedError("TODO(siddharth): freshness windows")


def is_fresh(observation: Observation, now: float) -> bool:
    """True if `observation` is within its property's freshness window at time `now`."""
    raise NotImplementedError("TODO(siddharth): is_fresh")
