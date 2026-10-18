"""The ONLY gateway from hidden truth to observations. Location-gated:
readings are produced only when the robot is AT the inspection point's location in the graph.
"""

from falkordb import Graph

from ripple.evidence.models import Observation
from ripple.graph import repository
from ripple.simulator import facility
from ripple.simulator.ground_truth import GroundTruth

UNITS = {"capacity": "units", "flow": "units", "temperature": "C"}


class NotAtInspectionPoint(Exception):
    """Raised when sensing is requested at an inspection point the robot is not at."""


def read(
    graph: Graph, truth: GroundTruth, robot_id: str, inspection_point_id: str, now: float
) -> list[Observation]:
    """Observations for every (asset, property) the inspection point covers; raises if robot isn't there."""
    targets = repository.inspection_targets(graph, robot_id, inspection_point_id)
    if not targets:
        raise NotAtInspectionPoint(f"{robot_id} is not at {inspection_point_id}")
    observations = []
    for t in targets:
        value = facility.observe(truth, t["asset_id"], t["property"])
        if value is None:
            continue
        observations.append(
            Observation(
                asset_id=t["asset_id"],
                property=t["property"],
                value=value,
                unit=UNITS.get(t["property"]),
                observed_at=now,
                ingested_at=now,
                quality=0.95,
                source="robot",
                produced_by=robot_id,
                mission_id=inspection_point_id,
            )
        )
    return observations
