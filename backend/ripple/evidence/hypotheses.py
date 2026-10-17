"""Rules deciding whether an observation SUPPORTS or CONTRADICTS a hypothesis.

SUPPORTS is evidence, not causation."""

from typing import Any, Literal

from ripple.evidence.models import Observation

Relation = Literal["SUPPORTS", "CONTRADICTS", "NEUTRAL"]


def classify(observation: Observation, hypothesis: dict[str, Any]) -> Relation:
    """Compare an observation against a hypothesis's EXPECTS pattern."""
    raise NotImplementedError("TODO(siddharth): support/contradict rules")
