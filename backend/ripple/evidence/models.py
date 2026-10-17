"""Evidence data models (Pydantic v2)."""

from pydantic import BaseModel


class Quality(BaseModel):
    """Reliability of an observation. TODO(siddharth): define fields."""


class Provenance(BaseModel):
    """Who/what produced an observation, where, and when. TODO(siddharth): define fields."""


class Observation(BaseModel):
    """A single measured fact about an asset property at a time. TODO(siddharth): define fields."""
