"""Incident lifecycle and decisions.

TODO(siddharth): route handlers."""

from fastapi import APIRouter

router = APIRouter(prefix="/incidents", tags=["incidents"])
