"""Index setup. Idempotent; safe to run on every startup.

FalkorDB syntax verified against the running instance: `CREATE INDEX FOR (n:L) ON (n.p)`;
re-creating an existing index raises "Attribute '<p>' is already indexed" (D-011).
Labels can't be query parameters, so the index DDL is built from the constant list below.
"""

from falkordb import Graph
from redis.exceptions import ResponseError

INDEXES: list[tuple[str, str]] = [
    ("Asset", "id"),
    ("Location", "id"),
    ("InspectionPoint", "id"),
    ("Action", "id"),
    ("Condition", "id"),
    ("Robot", "id"),
    ("Observation", "property"),
]


def ensure_schema(graph: Graph) -> None:
    """Create range indexes on the lookup keys used by graph/queries."""
    for label, prop in INDEXES:
        try:
            graph.query(f"CREATE INDEX FOR (n:{label}) ON (n.{prop})")
        except ResponseError as e:
            if "already indexed" not in str(e):
                raise
