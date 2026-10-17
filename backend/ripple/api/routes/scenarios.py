"""Load scenarios and inject faults.

TODO(siddharth): route handlers."""

from fastapi import APIRouter

router = APIRouter(prefix="/scenarios", tags=["scenarios"])
