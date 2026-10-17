"""The ONLY gateway from hidden truth to observations. Location-gated:
readings are produced only when the robot is at the relevant inspection point."""

from ripple.evidence.models import Observation
from ripple.simulator.ground_truth import GroundTruth


def read(truth: GroundTruth, robot_location: str, inspection_point_id: str, now: float) -> list[Observation]:
    """Return observations for an inspection point, or raise if the robot isn't there."""
    raise NotImplementedError("TODO(siddharth): location-gated sensor")
