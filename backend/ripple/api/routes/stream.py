"""WebSocket stream of live updates.

TODO(siddharth): route handlers."""

from fastapi import APIRouter

router = APIRouter(prefix="/stream", tags=["stream"])
