// Purpose:    Everything recorded about a Decision, for explanations (invariant #5: text derived only from this).
// Parameters: $decision_id
// Returns:    decision_id, summary, made_at, revision, incident_id, plans, evidence
// Used by:    ripple.graph.repository.decision_trace (M4)
MATCH (d:Decision {id: $decision_id})-[:TRIGGERED_BY]->(i:Incident)
OPTIONAL MATCH (d)-[:CONSIDERED]->(p:Plan)
OPTIONAL MATCH (d)-[rej:REJECTED]->(p)
OPTIONAL MATCH (d)-[sel:SELECTED]->(p)
WITH d, i, [x IN collect({plan: p.name, actions: p.actions, selected: sel IS NOT NULL,
                          rejected_reason: rej.reason}) WHERE x.plan IS NOT NULL] AS plans
OPTIONAL MATCH (d)-[:BASED_ON]->(o:Observation)-[:ABOUT]->(a:Asset)
WITH d, i, plans, [x IN collect({observation_id: o.id, asset_id: a.id, property: o.property,
                                 value: o.value, observed_at: o.observed_at, source: o.source})
                   WHERE x.observation_id IS NOT NULL] AS evidence
RETURN d.id AS decision_id, d.summary AS summary, d.made_at AS made_at, d.revision AS revision,
       i.id AS incident_id, plans, evidence
