"""Architecture invariants enforced as tests."""

import pytest


def test_ground_truth_not_imported_by_reasoning_layers() -> None:
    """agent/, planning/, evidence/ must not import ripple.simulator.ground_truth."""
    pytest.skip("TODO(siddharth): scan imports (e.g. via ast) and assert")


def test_cypher_only_in_repository() -> None:
    """Only graph/repository.py executes queries; no inline Cypher elsewhere."""
    pytest.skip("TODO(siddharth)")
