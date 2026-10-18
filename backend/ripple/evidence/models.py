"""Evidence data models (Pydantic v2).

An Observation is one measured fact about an asset property at a time, with provenance
(source, producer, quality). Observations are never overwritten; the latest per
(asset, property) is the current belief (DP1).
"""

from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

Source = Literal["robot", "sensor", "log", "predicted"]
Value = bool | int | float | str


class Observation(BaseModel):
    id: str = Field(default_factory=lambda: f"obs_{uuid4().hex[:10]}")
    asset_id: str
    property: str
    value: Value
    unit: str | None = None
    observed_at: float
    ingested_at: float | None = None
    quality: float = Field(default=1.0, ge=0.0, le=1.0)
    source: Source
    produced_by: str | None = None  # Sensor or Robot id
    incident_id: str | None = None
    mission_id: str | None = None
