"""Index / constraint setup. Idempotent; safe to run on every startup.

TODO(siddharth): check FalkorDB docs for index + constraint syntax."""

from falkordb import Graph


def ensure_schema(graph: Graph) -> None:
    """Create indexes on the lookup keys used by graph/queries (e.g. Asset id)."""
    raise NotImplementedError("TODO(siddharth): create indexes")
