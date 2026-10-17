"""Hypothetical intervention branches via GRAPH.COPY.

A branch is a *snapshot* of the main graph that a candidate plan's predicted effects are
written into. It is not a physics simulation. Branches must always be cleaned up.

TODO(siddharth): confirm GRAPH.COPY availability/semantics in the FalkorDB version we run."""

from collections.abc import Iterator
from contextlib import contextmanager

from falkordb import FalkorDB, Graph


def create_branch(db: FalkorDB, source: str, branch: str) -> Graph:
    """Copy graph `source` to `branch` and return the branch handle."""
    raise NotImplementedError("TODO(siddharth): GRAPH.COPY")


def delete_branch(db: FalkorDB, branch: str) -> None:
    """Delete a branch graph. Must never delete the main graph."""
    raise NotImplementedError("TODO(siddharth): delete branch")


@contextmanager
def branch(db: FalkorDB, source: str, name: str) -> Iterator[Graph]:
    """Context manager: create a branch, yield it, always delete on exit."""
    raise NotImplementedError("TODO(siddharth): branch lifecycle")
    yield  # pragma: no cover


def cleanup_orphan_branches(db: FalkorDB, prefix: str) -> list[str]:
    """Delete leftover branch graphs whose names start with `prefix`; return deleted names."""
    raise NotImplementedError("TODO(siddharth): orphan cleanup")
