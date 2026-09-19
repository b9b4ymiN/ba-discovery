# Requirements

## NEED-0001 — Consistent allocation reasoning
```yaml ba-record
id: NEED-0001
kind: NEED
status: CONFIRMED
importance: HIGH
derived_from: []
evidence: []
related: [REQ-0001, REQ-0002]
superseded_by: null
```
### Statement
Planners need a consistent, explainable way to prioritize orders when material is constrained.

## REQ-0001 — Recommend an allocation order
```yaml ba-record
id: REQ-0001
kind: REQUIREMENT
status: READY_FOR_DESIGN
importance: HIGH
derived_from: [NEED-0001]
evidence: []
related: [DEC-0001]
superseded_by: null
```
### Statement
The system shall recommend an order allocation sequence using the approved priority rules and show the reason for each material decision.
### Why
The planner must be able to review why the recommendation was made.
### Acceptance / Verification
Given constrained material and eligible orders, the recommendation shows the ordered candidates and the rules that affected each position.

## REQ-0002 — Preserve planner authority
```yaml ba-record
id: REQ-0002
kind: REQUIREMENT
status: READY_FOR_DESIGN
importance: HIGH
derived_from: [NEED-0001]
evidence: []
related: [DEC-0001, DEC-0002]
superseded_by: null
```
### Statement
The system shall allow the planner to accept or change the proposed allocation when policy permits.
### Acceptance / Verification
A planner can review and change a proposal, while named exceptional overrides require manager confirmation.

## CON-0001 — ERP remains system of record
```yaml ba-record
id: CON-0001
kind: CONSTRAINT
status: CONFIRMED
importance: HIGH
derived_from: []
evidence: []
related: []
superseded_by: null
```
### Statement
The project shall not replace the ERP as the source of truth for order and material data.
