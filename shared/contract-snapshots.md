# BA Discovery Snapshot Contract

Approved snapshots are **HISTORICAL** and append-only. Current truth remains in canonical records/project sections.

## Locations

Preferred v0.6 paths:

```text
.ba/phases/01-understand/R001.md
.ba/phases/02-requirements/R001.md
.ba/phases/03-design/R001.md
.ba/phases/04-spec/R001.md
```

Use monotonically increasing `RNNN.md`. Do not overwrite an approved revision. Existing legacy folder naming may remain; do not rewrite history merely for migration.

## Approval

Every v0.6+ approved snapshot contains:

```markdown
## Approval

**Status:** APPROVED | APPROVED_WITH_OPEN_ITEMS
**Approved by:** Current user
**Approved at:** <trusted timestamp when available; otherwise omit this line>
**Approval scope:**
- ...

**Open / excluded from approval:**
- ...

**Approval basis:** Explicit user approval in the active BA session.
```

Never invent a person name, timestamp, quotation, or approval scope. Legacy snapshots using older wording remain historical and are not rewritten solely for this terminology change. Legacy v0.5.1 snapshots without this block remain valid historical artifacts and are not rewritten solely to add it.

## Handoff to Next Phase

Every approved snapshot also contains a compact handoff:

```markdown
## Handoff to Next Phase

**Readiness:** READY | READY_WITH_OPEN_ITEMS | BLOCKED

**Approved summary:** 2–5 bullets.

**Must carry forward:** canonical IDs / evidence references only.

**Open items:** unresolved items that still matter.

**Known risks:** material risks only.

**Next focus:** the most valuable next step.

**Design Drivers:** Phase 2 only when useful; each driver references supporting IDs.

**Override / provenance notes:** only when a Soft Guard was bypassed.
```

`BLOCKED` is still a Soft Guard. Explicit override may proceed, but must not relabel the snapshot as READY.

## Bypassed prior-phase input

When proceeding without the preferred prior BA baseline, record phase input with all of:

- phase being entered,
- concrete source or source description,
- provenance (for example `USER_PROVIDED_APPROVED_INPUT`),
- validation status (for example `NOT_VALIDATED_BY_BA_REQUIREMENTS_PHASE`),
- optional user-authorized reason/notes.

A bypass never creates a fake prior baseline.
