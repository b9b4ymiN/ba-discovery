# Decisions

## DEC-0001 — Extend rather than replace the current data source
```yaml ba-record
id: DEC-0001
kind: DECISION
status: CONFIRMED
derived_from: [REQ-0001, CON-0001]
related: []
superseded_by: null
```
### Decision
Keep ERP-backed data as authoritative and add recommendation/explanation behavior around the existing flow.

## DEC-0002 — Planner authority with named manager exceptions
```yaml ba-record
id: DEC-0002
kind: DECISION
status: CONFIRMED
derived_from: [REQ-0002]
related: []
superseded_by: null
```
### Decision
Planners retain normal review authority; policy-defined high-impact moves require manager confirmation.
