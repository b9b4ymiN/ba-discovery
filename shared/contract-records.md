# BA Discovery Record Contract

## Record kinds

`REQUIREMENTS.md` owns:

- `NEED-*`
- `REQ-*`
- `CON-*`

`DECISIONS.md` owns `DEC-*`.

`RESEARCH.md` stores evidence synthesis/findings. Research is not project truth and never creates a requirement automatically.

## IDs

Use stable IDs such as `NEED-0001`, `REQ-0001`, `CON-0001`, `DEC-0001`.

**Next ID = highest numeric suffix among existing declarations of the same prefix + 1.**

Numeric gaps are valid. Duplicate/reused IDs for different meaning are invalid. Do not maintain a second counter source.

## Requirement lifecycle

`DISCOVERED → CLARIFYING → CANDIDATE → CONFIRMED → READY_FOR_DESIGN`

Additional states: `NEEDS_RECONFIRMATION`, `SUPERSEDED`, `REJECTED`.

A confirmed record's meaning is not silently rewritten. Material meaning change creates/supersedes explicitly while preserving history.

## Decision lifecycle

`PROPOSED`, `CONFIRMED`, `REJECTED`, `NEEDS_RECONFIRMATION`, `SUPERSEDED`.

Materiality heuristic: **Would we care later why this changed?** If yes, record the decision.

## Provenance and references

Keep explicit origin/evidence/reference fields where used. Formal references such as `derived_from` and `superseded_by` must resolve to declared canonical IDs or an existing `CHG-*` record when change provenance is used. Distinguish stakeholder statement, observed fact, estimate, research finding, inference, preference, assumption, and confirmed decision.

## Example requirement

```markdown
## REQ-0001 — Short title

```yaml ba-record
id: REQ-0001
kind: REQUIREMENT
status: CANDIDATE
importance: HIGH
origin: USER_NEED
derived_from: []
evidence: []
related: []
superseded_by: null
```

### Statement
...

### Why
...

### Acceptance / Verification
...
```


## v0.8 current-canonical rule

A semantic record whose meaning has been replaced must not remain in current canonical files merely with `status: SUPERSEDED`.

The replacement current record may use `derived_from: [CHG-0001]`.

A semantic replacement gets a new record ID. The applied `CHG-*` record preserves the Before → After mapping and the historical record remains available in change history and/or phase snapshots.
