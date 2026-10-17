"""RobotAdapter Protocol: the interface both mock and Cyberwave adapters implement.

TODO(siddharth): design methods in Step 0.3 (after reading Cyberwave SDK examples in 0.2)."""

from typing import Protocol


class RobotAdapter(Protocol):
    """Mobile inspection robot. Moves and reports state; does not manipulate equipment."""
