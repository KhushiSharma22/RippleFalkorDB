from functools import lru_cache
from ripple.config import get_settings
from falkordb import FalkorDB, Graph

@lru_cache(maxsize=1)

def get_db() -> FalkorDB:

    settings = get_settings()

    return FalkorDB(
        host=settings.falkordb_host,
        port=settings.falkordb_port,
    )

def get_graph(db: FalkorDB, name: str) -> Graph:
    return db.select_graph(name)

