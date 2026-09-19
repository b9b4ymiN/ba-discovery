---
project_name: Brownfield Capacity Planner
project_state: ACTIVE
current_phase: SPEC
current_activity: Final FRD approved
workflow_mode: PIPELINE
target_phase: SPEC
pipeline_status: COMPLETE
phase_inputs: []
---
# Brownfield Capacity Planner

## Problem
Planners can see overloaded capacity in the existing CSV workflow, but they cannot consistently explain which order should move first or when manager confirmation is required.

## Goal
Add explainable capacity recommendations while preserving ERP as the system of record and keeping policy authority with the business.

## Scope
### In
- Inspect the current planner workflow and reuse verified existing-system facts.
- Recommend which overloaded orders to review first.
- Explain the business rule behind each recommendation.
- Apply the approved manager-confirmation policy.

### Out
- Replacing ERP.
- Automatically releasing production changes without planner review.

## Current Understanding
- **Existing-system constraint:** ERP remains the source of truth for orders and machine capacity. Evidence: `existing-system/docs/current-workflow.md`.
- This fact was **not asked** from the stakeholder because the project evidence already answered it.
- **Stakeholder-only question:** which overload moves require manager confirmation? This is policy/authority knowledge, not a code fact.
- **Future requirement:** the recommendation must explain why an order is prioritized for review.

## Assumptions
- Daily export latency remains acceptable for the initial approved scope.

## Open Questions
- None blocking the approved example.

## Current Baselines
- Understand: .ba/phases/01-understand/R001.md
- Requirements: .ba/phases/02-requirements/R001.md
- Design: .ba/phases/03-design/R001.md
- Spec: .ba/phases/04-spec/R001.md

## Coverage
- ✓ Existing-system evidence inspected
- ✓ Problem and goal
- ✓ Existing-system constraint separated from future requirement
- ✓ Authority/policy question resolved by stakeholder
- ✓ Design and acceptance coverage

## Next Focus
Engineering planning outside BA Discovery.
