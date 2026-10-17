# RIPPLE

**An evidence-driven robot for preventing cascading equipment failures**

Team proposal · 14 October 2026 · FalkorDB + Cyberwave

---

## Overview

The way to make FalkorDB advanced here is to make the graph determine **what the robot investigates, which actions are feasible, and what consequences it expects.**

Ripple is an evidence-driven robot for preventing cascading equipment failures.

**The defining moment:** the robot discovers that the obvious fix would disrupt another machine, gathers the missing evidence, and finds an intervention that preserves service.

> The facility, capacities, and failure conditions below are proposed **simulation assumptions**, not claims about real industrial equipment.

---

## 1. The problem statement

In an interconnected facility, a local equipment fault can affect assets far beyond the location where the alarm appears. An overheating machine may depend on a shared cooling circuit; shutting down that circuit may interrupt other machines; an alternate supply may exist but have insufficient capacity or an unknown operational state.

Making the right intervention requires combining information that lives in different places:

- Physical connections between equipment.
- Operational dependencies and service priorities.
- Current observations and their reliability.
- Robot access and sensing capabilities.
- Action prerequisites and effects.
- Uncertainty about the actual cause of the fault.

**Target user:** a facility operator overseeing robotic inspection and incident response.

**Problem to solve:**

> How can a robot investigate an equipment fault and select a recovery sequence that preserves critical services, when infrastructure dependencies are interconnected and the available observations are incomplete or stale?

For the hackathon, we solve this in a small simulated cooling facility.

---

## 2. Our thesis

> A robot that reasons over an explicit graph of infrastructure, evidence, and action prerequisites can make better intervention decisions than a robot reacting only to local alarms. By selecting inspections that could change its decision, it can reduce uncertainty before acting and explain its choices through traceable graph paths.

This is a **hypothesis we will test**, not a result we should claim before evaluating it.

It has three parts:

1. **Connected reasoning:** A local fault must be evaluated against downstream consequences.
2. **Purposeful investigation:** The robot should inspect the missing facts that matter to its decision.
3. **Closed-loop recovery:** An action is successful only when subsequent observations confirm the intended effect.

**Technical contribution:** the combination of graph-based intervention planning and graph-guided evidence collection.

---

## 3. The concrete simulation

One mobile inspection robot and a compact facility containing:

- A primary cooling supply.
- A standby cooling supply.
- A main isolation valve.
- A bypass valve.
- A shared cooling header.
- Two machines: one critical, one lower priority.
- Inspection points for pump health, valve position, and flow.

The primary and standby branches both feed the shared header. For the MVP, model **directed flow with explicit capacity limits** and assume non-return protection. We will not attempt full hydraulic physics.

### Illustrative setup

| Element | Value |
|---|---|
| Critical machine A | requires 4 cooling units |
| Lower-priority machine B | requires 3 cooling units |
| Primary supply | normally provides 8 units |
| Standby supply | provides 8 or 5 units, depending on scenario |
| Fault | primary supply fails |
| Standby readiness | initially unknown |

These numbers create a meaningful decision:

- If standby capacity is **8**, both machines can remain operational.
- If standby capacity is **5**, the robot must reduce machine B's load before transferring supply.
- If standby is **unavailable**, the robot must choose an approved degraded-operation or shutdown sequence.

### Incident sequence

1. Machine A reports rising temperature.
2. Ripple traces its cooling dependencies.
3. The graph reveals that machine B shares the same supply.
4. Ripple identifies uncertainty about standby readiness.
5. The robot travels to an inspection point.
6. A new observation confirms readiness and capacity.
7. Ripple evaluates candidate intervention sequences.
8. It executes the selected sequence through simulated equipment controls.
9. It checks flow and temperature recovery.
10. If the expected recovery does not happen, it updates the evidence and replans.

> **Important scope choice:** The mobile robot performs **inspection**. Equipment intervention occurs through **simulated controllable valves and supplies**. Physical valve manipulation is a later extension.

That makes the embodiment meaningful without making robot-arm integration the entire project.

---

## 4. What the user sees

The interface shows three connected views:

- **The facility:** robot movement, equipment state, cooling flow, and fault injection controls.
- **The relevant graph:** only the dependencies, observations, and actions involved in the current decision.
- **The decision trace:** what Ripple knows, what it still needs to inspect, which plans were rejected, and why.

Example explanation before inspection:

> "Closing the main supply now would interrupt cooling to both machines. Standby capacity is unverified. I'm inspecting the standby branch before deciding whether both loads can remain active."

After inspection:

> "Standby capacity is 5 units; current demand is 7. Reduce machine B's load, activate standby, verify flow, then isolate the failed primary branch."

These explanations must be **generated from recorded query results and checks**, not invented after execution.

---

## 5. The advanced FalkorDB design

One connected operational graph with several types of relationships. Temporary scenario graphs hold hypothetical changes.

### A. Infrastructure and dependency relationships

Model assets, ports or junctions, services, and locations.

Example relationships:

- `FEEDS`
- `REQUIRES_SERVICE`
- `LOCATED_IN`
- `CONNECTED_TO`
- `HAS_CAPABILITY`

The distinction between physical and operational relationships matters. A pipe connection means equipment is connected; it does **not** automatically mean sufficient cooling is available.

Queries answer:

- Which machines depend on this branch?
- Which alternate supplies can reach them?
- Which assets are affected if this valve closes?
- Which affected services are critical?

Capacity and allocation calculations sit in our planner, using topology retrieved from FalkorDB.

### B. Evidence with time and provenance

Store observations as **separate nodes** rather than continually overwriting a single equipment status.

An observation contains:

- Asset and property observed.
- Value and unit.
- Observation time and ingestion time.
- Sensor or source identity.
- Quality or confidence indicator.
- Inspection or mission identifier.

Relationships:

```
(Observation)-[:ABOUT]->(Asset)
(Observation)-[:PRODUCED_BY]->(Sensor)
(Observation)-[:SUPPORTS | :CONTRADICTS]->(Hypothesis)
```

This lets us distinguish *"The valve was reported open earlier"* from *"The robot confirmed the valve is open during this incident."*

Freshness rules depend on the property. A physical connection changes slowly; valve position can change immediately.

Temporal validity and evidence reconciliation are **logic we implement over the graph**, not an automatic database capability.

### C. Explicit fault hypotheses

Maintain a small set of possible explanations:

- Primary supply failure.
- Restricted flow.
- Incorrect valve state.
- Faulty temperature observation.

Each hypothesis connects to expected observations and possible inspections. The robot can ask:

> "Which observation would distinguish the remaining explanations?"

For the MVP, use transparent rules and a few discrete hypotheses. We do not need a learned probabilistic model.

Crucially, a `SUPPORTS` edge is **evidence** for a hypothesis; it does not prove causation.

### D. Actions with multiple prerequisites

Represent an action as a node connected to condition nodes. For example, *isolate primary supply* may require:

- Standby supply active.
- Bypass verified open.
- Adequate delivered cooling.
- Current demand within available capacity.

Every required condition must hold.

A graph traversal identifies the conditions; our validator checks their values, evidence freshness, and consistency. This avoids treating "there is a path to this action" as proof that the action is executable.

This is a powerful advanced use of the graph: planning over dependencies between actions and world conditions.

### E. Hypothetical intervention branches

Create a graph snapshot for each candidate plan:

1. Isolate primary immediately.
2. Activate standby, verify flow, then isolate primary.
3. Reduce noncritical load, activate standby, verify flow, then isolate primary.

Apply the proposed changes to each branch and evaluate the consequences.

FalkorDB documents `GRAPH.COPY` for copying graphs, including a consistent snapshot of the source. That gives us a concrete mechanism for scenario branching. Our own transition model supplies the action effects and predicted outcomes. [1]

Copying a graph does **not** simulate physics. The distinction should be clear in our implementation and pitch.

Start with three branches and a short planning horizon. Avoid copying the entire history for every hypothetical action once the graph grows.

### F. Decision provenance

Create a `Decision` node linked to:

- The triggering incident.
- Observations considered.
- Graph state revision.
- Candidate plans.
- Rejected constraints.
- Selected action sequence.
- Execution results.
- Verification observations.

This becomes a queryable record of what the system knew and why it acted. The explanation panel displays this record directly.

---

## 6. How ScoutMind becomes part of Ripple

The robot should inspect the fact with the greatest potential to improve its decision.

Conceptual objective:

> **Inspection value** = expected improvement in the intervention decision − inspection cost − cost of delaying recovery

For the MVP, use a simpler, explainable approximation:

- Does this unknown fact block a promising plan?
- Could checking it eliminate a harmful candidate?
- How many critical dependencies does it affect?
- How long will the inspection take?
- Can another available sensor answer it more cheaply?

For example:

- Rechecking machine A's temperature may confirm the alarm.
- Checking standby capacity may determine the entire recovery strategy.

Ripple should choose the second inspection when it is the decision-critical uncertainty.

Do not call this calibrated information gain unless we actually implement a probability model. **"Decision relevance score"** is a defensible name for the initial heuristic.

---

## 7. The runtime architecture

Core loop:

```
Observe → update evidence → query dependencies → identify uncertainty → inspect
        → evaluate plans → validate → execute → verify
```

Responsibilities:

| Component | Responsibility |
|---|---|
| Cyberwave adapter | Robot commands, robot state, and supported inspection interfaces |
| Facility simulator | Simplified cooling capacity, valve states, machine demand, temperature trends, injected faults |
| FalkorDB | Infrastructure, observations, hypotheses, prerequisites, scenario branches, decision records |
| Planner | Candidate generation, consequence evaluation, inspection selection, constraint checks |
| Agent layer | Tool selection and operator-facing explanations |
| Interface | Facility view, graph paths, execution history |

Cyberwave's SDK examples document simulated locomotion without physical hardware, but require backend access and an API key. Camera and other capabilities must be verified for the selected environment. [2]

The first integration milestone must prove that a simulated robot can **move** and that we can **read its resulting state**. Installing the SDK alone does not establish that.

If rendered sensing is unavailable, use explicitly labelled synthetic inspection readings that become available only when the robot reaches the inspection location. That still supports an honest embodied decision-making demonstration.

---

## 8. How to keep the simulation credible

**Separate the simulator's hidden ground truth from the agent's knowledge.** The simulator knows whether the standby pump is actually faulty. The agent learns about it only through an allowed observation. Otherwise, the system could appear to investigate while silently reading the answer.

**Separate predicted state from observed state:**

- Sending "open valve" creates an execution attempt.
- Receiving an acknowledgement confirms receipt.
- A state observation confirms that the valve opened.
- Flow verification confirms the intended operational effect.

Before executing each action, **recheck its prerequisites against the latest graph revision.** A plan that was valid before a new fault may no longer be valid.

---

## 9. Planning and agent tools

A small set of structured tools:

- `get_affected_assets(asset_id)`
- `get_missing_evidence(plan_id)`
- `rank_inspections(incident_id)`
- `request_inspection(target_id)`
- `evaluate_plan(plan_id, state_revision)`
- `validate_next_action(action_id, state_revision)`
- `execute_simulated_action(action_id)`
- `verify_recovery(incident_id)`

These are our interfaces, optionally exposed through MCP.

The agent can choose tools and interpret results. **Deterministic checks enforce action prerequisites and operating constraints.**

Use a bounded planner for the first version: a handful of action types and short sequences. Hard constraints reject infeasible plans first; remaining plans are ranked by service preservation, recovery time, and inspection effort.

---

## 10. What we should build first

**Milestone 1: a complete vertical slice.**
One fault, one inspection, one graph query, one intervention, and one verified outcome. Success means the robot's observation changes the action chosen.

**Milestone 2: connected consequences.**
Add the second machine and the shared cooling dependency. Show that isolating the primary branch immediately creates an unacceptable downstream effect.

**Milestone 3: evidence-driven planning.**
Add stale standby data, inspection selection, and alternative recovery sequences.

**Milestone 4: hypothetical branches and explanations.**
Compare candidate plans in graph copies. Display why each rejected plan failed.

**Milestone 5: evaluation and demo polish.**
Add fault injection, repeatable scenarios, metrics, and a concise narrated demo.

For a four-day event, keep **multi-robot coordination, learned perception, full fluid dynamics, and physical manipulation** outside the initial scope.

---

## 11. How we prove that the graph matters

Run the same scenarios against three configurations:

1. **Local-response baseline:** reacts to the alarm with a fixed recovery rule.
2. **Graph planner without active inspection:** sees dependencies but relies on existing evidence.
3. **Full Ripple:** uses dependencies and gathers decision-critical evidence.

Test conditions:

- Standby healthy with enough capacity.
- Standby healthy with insufficient capacity.
- Standby unavailable.
- Stale valve-state observation.
- Valve command fails to change state.
- New equipment dependency added before the incident.

Metrics:

- Successful recovery rate.
- Critical-service interruption duration.
- Operating-constraint violations.
- Time to verified recovery.
- Number of inspections.
- Planning and graph-query latency.

The especially convincing test is **changing the topology without changing the recovery code.** If connecting another load changes the chosen intervention, viewers can see that the graph governs the decision.

These are evaluation plans, not results we have already achieved.

---

## 12. The demo and pitch

The demo lets a viewer inject a fault and alter standby readiness or capacity. Then show:

1. The fault appears.
2. The relevant dependency paths light up.
3. Ripple identifies the missing evidence.
4. The robot moves to inspect.
5. Candidate intervention outcomes appear.
6. Ripple executes the chosen sequence.
7. The resulting observations confirm recovery, or trigger replanning.

**Pitch:**

> Ripple gives an inspection robot the context to intervene. It connects infrastructure dependencies, live evidence, and action prerequisites in FalkorDB, then uses Cyberwave to investigate and execute in simulation. Before changing the world, it checks what else will change with it.

**Recommendation:** commit to four core differentiators: **multi-hop impact analysis, evidence freshness, decision-driven inspection, and hypothetical intervention branches.** Together, they make FalkorDB central to the robot's behavior and give us a focused project we can start developing immediately.

---

## Sources

1. FalkorDB `GRAPH.COPY`: https://docs.falkordb.com/commands/graph.copy
2. Cyberwave SDK examples: https://github.com/cyberwave-os/cyberwave-python/blob/main/examples/README.md
