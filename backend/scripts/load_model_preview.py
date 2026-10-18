"""Load docs/graph-model-preview.cypher into the throwaway graph `model_preview` (dev tooling)."""

from pathlib import Path

from redis.exceptions import ResponseError

from ripple.graph.client import get_db, get_graph

CYPHER = Path(__file__).resolve().parents[2] / "docs" / "graph-model-preview.cypher"

db = get_db()
g = get_graph(db, "model_preview")
try:
    g.delete()
except ResponseError as e:
    if "empty key" not in str(e):
        raise

query = "\n".join(line for line in CYPHER.read_text().splitlines() if not line.lstrip().startswith("//"))
stats = g.query(query)
print(f"model_preview: {stats.nodes_created} nodes, {stats.relationships_created} relationships")
