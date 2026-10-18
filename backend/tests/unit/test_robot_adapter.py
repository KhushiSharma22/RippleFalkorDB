from ripple.robot.base import Pose, RobotAdapter, arrived
from ripple.robot.mock_adapter import MockRobotAdapter


def test_mock_satisfies_protocol() -> None:
    assert isinstance(MockRobotAdapter(), RobotAdapter)


def test_move_then_verify_by_readback() -> None:
    robot = MockRobotAdapter()
    target = Pose(1.5, -0.5)
    robot.move_to(target)
    assert arrived(robot.current_pose(), target)
    assert robot.commands == [target]


def test_injected_failure_is_detected_by_readback() -> None:
    robot = MockRobotAdapter(start=Pose(0.0, 0.0))
    robot.fail_next_moves(1)
    target = Pose(2.0, 0.0)
    robot.move_to(target)
    assert robot.commands == [target]  # command was sent...
    assert not arrived(robot.current_pose(), target)  # ...but readback shows no arrival
    robot.move_to(target)  # retry succeeds
    assert arrived(robot.current_pose(), target)


def test_unknown_pose_is_not_arrived() -> None:
    assert not arrived(None, Pose(0.0, 0.0))
    assert not arrived(MockRobotAdapter(start=None).current_pose(), Pose(0.0, 0.0))


def test_arrival_tolerance() -> None:
    assert arrived(Pose(0.05, 0.0), Pose(0.0, 0.0), tol=0.1)
    assert not arrived(Pose(0.2, 0.0), Pose(0.0, 0.0), tol=0.1)
