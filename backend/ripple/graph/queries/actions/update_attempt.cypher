// Purpose:    Record the command acknowledgement (a receipt, still not proof of effect).
// Parameters: $id, $status ('acked' | 'rejected'), $ack_at
// Returns:    status
// Used by:    ripple.graph.repository.update_attempt
MATCH (x:ExecutionAttempt {id: $id})
SET x.status = $status, x.ack_at = $ack_at
RETURN x.status AS status
