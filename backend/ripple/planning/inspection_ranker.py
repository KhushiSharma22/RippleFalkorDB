"""Decision relevance score: how likely an inspection is to change the chosen plan (M3).

Honest naming: a transparent heuristic, not calibrated information gain. For each reachable
inspection point (all from graph queries):

    score = 3.0 * blocks       # undecided candidate plans waiting on evidence this point provides
          + 1.0 * critical     # critical services downstream of the assets it observes
          + 0.5 * hypotheses   # open fault hypotheses it distinguishes
          - 0.05 * travel_cost # ADJACENT_TO route cost from the robot (algo.SPpaths)

A point with blocks == 0 cannot change the decision; the orchestrator never travels for it.
"""

from dataclasses import dataclass, field

from falkordb import Graph

from ripple.graph import repository

W_BLOCKS, W_CRITICAL, W_HYPOTHESES, W_TRAVEL = 3.0, 1.0, 0.5, 0.05

Item = tuple[str, str]  # (asset_id, property)


@dataclass
class InspectionCandidate:
    ip_id: str
    location_id: str
    covers: list[Item] = field(default_factory=list)
    plans: list[str] = field(default_factory=list)
    critical: int = 0
    hypotheses: int = 0
    travel_cost: float = 0.0
    score: float = 0.0

    @property
    def blocks(self) -> int:
        return len(self.plans)

    def summary(self) -> dict:
        return {
            "ip_id": self.ip_id,
            "score": round(self.score, 2),
            "blocks": self.plans,
            "covers": [f"{a}.{p}" for a, p in self.covers],
            "critical": self.critical,
            "hypotheses": self.hypotheses,
            "travel_cost": self.travel_cost,
        }


def rank_inspections(
    graph: Graph, robot_id: str, incident_id: str, missing_by_plan: dict[str, list[Item]]
) -> list[InspectionCandidate]:
    """Reachable inspection points, best decision relevance score first."""
    candidates: dict[str, InspectionCandidate] = {}
    for plan, items in missing_by_plan.items():
        for item in items:
            for ip in repository.inspection_points_for(graph, *item):
                c = candidates.setdefault(
                    ip["ip_id"], InspectionCandidate(ip["ip_id"], ip["location_id"])
                )
                if item not in c.covers:
                    c.covers.append(item)
                if plan not in c.plans:
                    c.plans.append(plan)
    for row in repository.distinguishing_inspections(graph, incident_id):
        c = candidates.setdefault(
            row["ip_id"], InspectionCandidate(row["ip_id"], row["location_id"])
        )
        c.hypotheses = int(row["n_hypotheses"])

    ranked = []
    for c in candidates.values():
        route = repository.route_to_inspection_point(graph, robot_id, c.ip_id)
        if route is None:
            continue  # unreachable from the robot's current location
        c.travel_cost = float(route["cost"])
        services = {
            s["service_id"]
            for asset_id in {a for a, _ in c.covers}
            for s in repository.critical_services_affected(graph, asset_id)
        }
        c.critical = len(services)
        c.score = (
            W_BLOCKS * c.blocks
            + W_CRITICAL * c.critical
            + W_HYPOTHESES * c.hypotheses
            - W_TRAVEL * c.travel_cost
        )
        ranked.append(c)
    return sorted(ranked, key=lambda c: (-c.score, c.travel_cost, c.ip_id))
