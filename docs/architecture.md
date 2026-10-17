# Architecture

TODO(siddharth): components, responsibilities, data flow.

## Core loop
Observe → update evidence → query dependencies → identify uncertainty → inspect →
evaluate plans → validate → execute → verify (→ replan on failure).

## Invariants
1. The graph is load-bearing (all topology/evidence/prerequisites via `graph/queries/`).
2. Hidden truth is hidden (`simulator.ground_truth` never imported by agent/planning/evidence).
3. Predicted ≠ observed (attempt → ack → state observation → effect observation).
4. Recheck against latest `StateRevision` before every action.
5. Explanations are derived from recorded Decision data only.
