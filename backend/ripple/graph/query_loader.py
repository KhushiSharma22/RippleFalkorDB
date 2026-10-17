"""Loads named Cypher queries from graph/queries/<area>/<name>.cypher."""

from pathlib import Path

QUERIES_DIR = Path(__file__).parent / "queries"


def load_query(name: str) -> str:
    """Return query text for a name like "impact/affected_assets".

    Raises FileNotFoundError for unknown names. May cache.
    """
    raise NotImplementedError("TODO(siddharth): load .cypher by name")
