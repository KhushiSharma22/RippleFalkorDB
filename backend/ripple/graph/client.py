"""FalkorDB connection and graph selection."""

from falkordb import FalkorDB, Graph

from ripple.config import Settings


def get_db(settings: Settings) -> FalkorDB:
    """Return a connected FalkorDB client for settings.falkordb_host/port."""
    raise NotImplementedError("TODO(siddharth): connect to FalkorDB")


def get_graph(db: FalkorDB, name: str) -> Graph:
    """Select a graph by name (main graph or a branch created by branching.py)."""
    raise NotImplementedError("TODO(siddharth): select graph")
