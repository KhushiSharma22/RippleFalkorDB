"""Rules deciding whether an observation SUPPORTS or CONTRADICTS a hypothesis.

Transparent rule: a hypothesis EXPECTS (asset, property, op, value). A matching observation
supports it; a mismatching one contradicts it. SUPPORTS is evidence, not causation.
"""

from typing import Any, Literal

from ripple.evidence.beliefs import compare
from ripple.evidence.models import Observation

Relation = Literal["SUPPORTS", "CONTRADICTS"]


def classify(observation: Observation, expectation: dict[str, Any]) -> tuple[Relation, str]:
    """Compare an observation with one EXPECTS pattern {op, value}; return (relation, rule text)."""
    rule = f"{observation.asset_id}.{observation.property} {expectation['op']} {expectation['value']!r}"
    matches = compare(expectation["op"], observation.value, expectation["value"])
    return ("SUPPORTS" if matches else "CONTRADICTS"), rule
