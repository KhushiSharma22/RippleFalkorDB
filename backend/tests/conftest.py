import uuid

import pytest
from redis.exceptions import ConnectionError, ResponseError

from ripple.config import get_settings
from ripple.graph.client import get_db, get_graph


@pytest.fixture(scope="session")
def db():

    db = get_db()

    try:
        db.connection.ping()
    except ConnectionError:
        s = get_settings()
        pytest.fail(
            f"Cannot connect to FalkorDB at {s.falkordb_host}:{s.falkordb_port}. Is it running?"
        )
    return db


@pytest.fixture(scope="session")
def graph(db, request):

    name = f"test_{request.node.name}_{uuid.uuid4().hex[:6]}"
    g = get_graph(db, name)
    yield g
    try:
        g.delete()
    except ResponseError as e:
        if "empty key" not in str(e):
            raise
