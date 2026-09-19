---
project_name: Order Allocation Planner
project_state: ACTIVE
current_phase: SPEC
current_activity: Final FRD approved
workflow_mode: PIPELINE
target_phase: SPEC
pipeline_status: COMPLETE
phase_inputs:
  - phase: DESIGN
    source: stakeholder-provided approved priority matrix
    provenance: USER_PROVIDED_APPROVED_INPUT
    validation: CROSS_CHECKED_AGAINST_BA_REQUIREMENTS_PHASE
---
# Order Allocation Planner

## Problem
When material is insufficient for every order, planners currently combine spreadsheet checks and personal judgment, which makes priority reasoning inconsistent and hard to explain.

## Goal
Give planners a traceable recommendation while preserving final planner authority and named manager-confirmation exceptions.

## Scope
### In
- Prepare eligible orders for allocation.
- Apply approved priority rules.
- Explain the recommendation.
- Allow planner review and permitted override.

### Out
- Fully autonomous production release.
- Replacing the ERP system of record.

## Current Understanding
- The ERP remains the source of truth for orders and material availability.
- Planner remains final authority for normal allocation decisions.

## Assumptions
- Peak active planner count is estimated at ~30 and is not a hard capacity requirement yet.

## Open Questions
- None blocking the approved v0.6 example scope.

## Current Risks
- Priority-matrix ownership must stay explicit as business policy changes.

## Current Baselines
- Understand: .ba/phases/01-understand/R001.md
- Requirements: .ba/phases/02-requirements/R001.md
- Design: .ba/phases/03-design/R001.md
- Spec: .ba/phases/04-spec/R001.md

## Coverage
- ✓ Current workflow
- ✓ Problem
- ✓ Goal
- ✓ Constraints
- ✓ Design drivers

## Next Focus
Engineering planning outside BA Discovery.
