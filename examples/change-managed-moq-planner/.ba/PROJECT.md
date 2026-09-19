---
project_name: Change-Managed MOQ Planner
current_phase: SPEC
workflow_mode: DIRECT
target_phase: NONE
pipeline_status: PAUSED
phase_inputs: []
---
# Change-Managed MOQ Planner

## Problem
The planner must apply the correct MOQ rule without confusing pending changes with approved behavior.

## Goal
Keep current approved planning truth clean while preserving why MOQ behavior evolved.

## Current Understanding
- Current approved MOQ is determined by Package Size.
- A separate capacity change is still pending and is not current truth.

## Current Baselines
- Requirements: .ba/phases/02-requirements/R001.md

## Next Focus
Review CHG-0002 impact when the user is ready.
