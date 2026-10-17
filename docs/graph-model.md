# Graph data model (v1)

> Written by Siddharth (Step 0.4). Draft starting point is in CLAUDE.md §6.

## Node labels
TODO(siddharth): label, key property, other properties, why it's a node (not a property).

## Relationships
TODO(siddharth): type, from → to, properties, direction rationale.

## Diagram
TODO(siddharth)

## Key distinctions
- Physical connection (`CONNECTED_TO`) ≠ operational sufficiency (capacity math in `planning/capacity.py`).
- `SUPPORTS` / `CONTRADICTS` are evidence relations, not causation.
