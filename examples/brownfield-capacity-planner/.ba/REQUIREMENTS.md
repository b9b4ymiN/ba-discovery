# Requirements

## NEED-0001 — Explain overload priorities
```yaml ba-record
id: NEED-0001
kind: NEED
status: CONFIRMED
derived_from: []
related: [REQ-0001]
superseded_by: null
```
### Statement
Planners need a consistent and explainable way to decide which overloaded orders to review first.

## REQ-0001 — Explain recommendation
```yaml ba-record
id: REQ-0001
kind: REQUIREMENT
status: READY_FOR_DESIGN
derived_from: [NEED-0001]
related: [DEC-0001]
superseded_by: null
```
### Statement
The system shall show the reason each overloaded order is prioritized for planner review.
### Acceptance / Verification
Given multiple overloaded orders, each recommendation shows the business rule that affected its priority.

## REQ-0002 — Apply manager-confirmation policy
```yaml ba-record
id: REQ-0002
kind: REQUIREMENT
status: READY_FOR_DESIGN
derived_from: []
related: [DEC-0002]
superseded_by: null
```
### Statement
The system shall require manager confirmation for the overload-move cases approved by the operations stakeholder.
### Acceptance / Verification
A move categorized as manager-controlled cannot be confirmed by a planner alone.

## CON-0001 — ERP remains source of truth
```yaml ba-record
id: CON-0001
kind: CONSTRAINT
status: CONFIRMED
derived_from: []
related: [DEC-0001]
superseded_by: null
```
### Statement
ERP remains the system of record for production orders and machine capacity.
### Evidence
`existing-system/docs/current-workflow.md` and `existing-system/src/planner.py`.
