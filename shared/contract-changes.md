# BA Discovery Change Contract

## Single User Only

BA Discovery has one interactive BA user per project/run. That same user supplies business intent, clarification, impact confirmation, and final confirmation. Domain roles inside the system being designed do not become BA-workflow participants.

## Durable staging

Open changes live at `.ba/changes/CHG-NNNN.md`.

An open change is durable working analysis and **not canonical truth**.

Every v0.8 change begins with:

```yaml
---
contract_version: 0.8
change_id: CHG-0001
status: PROPOSED
impact_level: IMPACT_UNKNOWN
impact_confirmation: PENDING
final_confirmation: PENDING
post_commit_verification: PENDING
blocking_status: CLEAR
---
```

Allowed `status` values:

`PROPOSED`, `ANALYZING`, `AWAITING_IMPACT_CONFIRMATION`, `IMPACT_CONFIRMED`, `REVALIDATING`, `AWAITING_FINAL_CONFIRMATION`, `APPLIED`, `CANCELLED`, `SUPERSEDED`.

Allowed `impact_level` values:

`NON_SEMANTIC`, `LOCAL`, `PROPAGATING`, `FOUNDATIONAL`, `IMPACT_UNKNOWN`.

Confirmation values:

- `impact_confirmation`: `PENDING | CONFIRMED`
- `final_confirmation`: `PENDING | CONFIRMED`
- `post_commit_verification`: `PENDING | VERIFIED`
- `blocking_status`: `CLEAR | BLOCKED`

## Required human sections

Every open or applied change keeps these headings:

- `## What is changing?`
- `## Why are we changing this?`
- `## Change Identity`
- `## Impact`
- `## Revalidation`
- `## Candidate Truth`
- `## Final Confirmation`

Applied changes additionally contain `## Applied Result`.

Human-readable meaning comes first; record IDs and dependency details are traceability underneath.

## Change identity

When new intent arrives, read actual OPEN change files first.

Classify:

- `MATCH_EXISTING`
- `NEW_CHANGE`
- `UNCERTAIN`

Change identity is anchored by business intent, not wording, keyword overlap, record count, or shared implementation component.

Multiple OPEN changes may exist. Review all OPEN changes for identity, but keep one focused change at a time. If new intent appears to match more than one OPEN change, do not merge them automatically; clarify the business intent first.

## Impact

Impact levels are proposed by AI with reasons and evidence, then confirmed by the single user.

Affected records may be:

- `AFFECTED_BUT_STILL_VALID`
- `NEEDS_UPDATE`
- `NEEDS_RECONFIRMATION`
- `SUPERSEDED`

Affected does not mean invalid.

## Confirmation and mutation

`IMPACT_CONFIRMED` is not final change approval.

Approved canonical truth remains unchanged until:

1. impact has been confirmed,
2. minimum revalidation is complete,
3. the user confirms the final Before → After,
4. prospective state passes deterministic integrity validation,
5. canonical state is committed,
6. canonical state is read back and verified.

**Stage the change, commit the truth.**

**Preserve confirmed understanding; revalidate only the delta.**

**Current truth for work. History on demand.**
