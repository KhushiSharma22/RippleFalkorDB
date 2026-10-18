"""Per-property freshness windows: how long an observation of a property stays usable.

Windows are synthetic simulation assumptions: things that can change instantly (valve
position, flow, running state) go stale fast; slower-changing facts (pump health,
capacity) last longer.
"""

FRESHNESS_WINDOWS_S: dict[str, float] = {
    "position": 120.0,
    "running": 120.0,
    "flow": 60.0,
    "temperature": 60.0,
    "health": 600.0,
    "capacity": 600.0,
}
DEFAULT_WINDOW_S = 300.0


def freshness_window(prop: str) -> float:
    """Seconds an observation of `prop` stays fresh."""
    return FRESHNESS_WINDOWS_S.get(prop, DEFAULT_WINDOW_S)


def is_fresh(prop: str, observed_at: float, now: float) -> bool:
    """True if an observation of `prop` made at `observed_at` is still usable at `now`."""
    return now - observed_at <= freshness_window(prop)
