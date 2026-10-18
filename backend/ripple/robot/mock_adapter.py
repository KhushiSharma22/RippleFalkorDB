"""In-process MockRobotAdapter so development never blocks on Cyberwave.

Teleports to the commanded target. Failures can be injected so the orchestrator's
verify/replan path is testable without a real robot.
"""

from ripple.robot.base import Pose

ORIGIN = Pose(0.0, 0.0)


class MockRobotAdapter:
    """RobotAdapter that teleports instantly, with optional injected move failures."""

    def __init__(self, start: Pose | None = ORIGIN) -> None:
        self._pose = start
        self._fail_next_moves = 0
        self.commands: list[Pose] = []  # every commanded target, for test assertions

    def current_pose(self) -> Pose | None:
        return self._pose

    def move_to(self, target: Pose) -> None:
        self.commands.append(target)
        if self._fail_next_moves > 0:
            self._fail_next_moves -= 1
            return  # command "accepted" but robot stays put
        self._pose = target

    def fail_next_moves(self, n: int = 1) -> None:
        """Make the next `n` move_to calls silently not move the robot."""
        self._fail_next_moves = n
