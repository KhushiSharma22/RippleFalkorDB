"""Relevant-subgraph views for the UI.

TODO(siddharth): route handlers."""

from fastapi import APIRouter

router = APIRouter(prefix="/graph", tags=["graph"])
