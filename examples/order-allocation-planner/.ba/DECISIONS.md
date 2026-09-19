# Decisions

## DEC-0001 — Recommendation, not autonomous release
```yaml ba-record
id: DEC-0001
kind: DECISION
status: CONFIRMED
derived_from: [REQ-0001, REQ-0002]
superseded_by: null
```
The system recommends; the planner remains the normal final decision maker.

## DEC-0002 — Manager confirms named exceptional overrides
```yaml ba-record
id: DEC-0002
kind: DECISION
status: CONFIRMED
derived_from: [REQ-0002]
superseded_by: null
```
Overrides classified by policy as exceptional require manager confirmation before finalization.
