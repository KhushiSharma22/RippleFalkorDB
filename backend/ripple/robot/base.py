"""RobotAdapter Protocol: the interface both mock and Cyberwave adapters implement.

Design (D-005, D-007): the adapter knows coordinates, not topology. Location (x, y) lives
on `Location` nodes in the graph; the orchestrator decides where to go. The adapter only
*commands* a move and *reports* a pose. Arrival is a separate check (`arrived`), so a
command is never mistaken for an outcome (predicted != observed).
"""

import math
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class Pose:
    """Planar robot pose in facility coordinates (metres)."""

    x: float
    y: float


@runtime_checkable
class RobotAdapter(Protocol):
    """Mobile inspection robot. Moves and reports pose; does not manipulate equipment."""

    def current_pose(self) -> Pose | None:
        """Latest observed pose, or None if no pose is known."""
        ...

    def move_to(self, target: Pose) -> None:
        """Command a move to `target`. Makes no claim that the move succeeded."""
        ...


def arrived(pose: Pose | None, target: Pose, tol: float = 0.1) -> bool:
    """True if an observed `pose` is within `tol` metres of `target`. Unknown pose = not arrived."""
    if pose is None:
        return False
    return math.hypot(pose.x - target.x, pose.y - target.y) <= tol
