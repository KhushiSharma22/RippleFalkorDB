"""Loads named Cypher queries from graph/queries/<area>/<name>.cypher."""

from functools import lru_cache
from pathlib import Path

QUERIES_DIR = Path(__file__).parent / "queries"


@lru_cache
def load_query(name: str) -> str:
    """Return query text for a name like "impact/affected_assets".

    Raises FileNotFoundError for unknown names. Cached: files are read once per process.
    """
    path = QUERIES_DIR / f"{name}.cypher"
    if not path.is_file():
        raise FileNotFoundError(f"Unknown query: {name} ({path})")
    return path.read_text()
