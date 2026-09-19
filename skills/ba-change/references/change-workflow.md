# Change Workflow

## 1. Change Identity Review

- Read the actual OPEN `CHG-*` files before deciding whether the new intent belongs to an existing change.
- Classify `MATCH_EXISTING | NEW_CHANGE | UNCERTAIN`.
- Business intent is the anchor, not wording, keyword overlap, record count, or shared implementation component.
- Multiple OPEN changes may exist, but keep one focused change at a time.
- If new intent appears to match more than one OPEN change, do not auto-merge; clarify the user's business intent.
- If matching, update the same CHG and run Delta Impact Review.
- If uncertain, ask one user-world intent question rather than asking the user to classify records.

## 2. Durable Staging

- `CHG-*` is editable while open.
- `AWAITING_*` is a normal pause state; time to think is valid state.
- Pending meaning never becomes canonical automatically.
- On resume, read the durable CHG and continue from its status/Next Focus instead of re-interviewing from the beginning.

## 3. Focused Evidence Traversal

- Read the change.
- Read directly relevant current canonical truth.
- Follow actual references, code, docs, schema, API, or other evidence only when the causal link requires it.
- Code/docs describe current implementation reality; they do not automatically override approved business truth.
- Search can locate evidence; keyword similarity is not impact proof.
- Stop when causal propagation stops.

Causal test: if the change occurs, can the item become incorrect, incomplete, require reinterpretation, or behave differently because of this change? If no, do not expand the frontier.

## 4. Impact Frontier

Affected items use:

`AFFECTED_BUT_STILL_VALID | NEEDS_UPDATE | NEEDS_RECONFIRMATION | SUPERSEDED`.

Propose one qualitative level:

`NON_SEMANTIC | LOCAL | PROPAGATING | FOUNDATIONAL | IMPACT_UNKNOWN`.

`IMPACT_UNKNOWN` means inspect/research/clarify; do not guess severity or invent a numeric impact/confidence score.

## 5. Impact Comprehension

Before confirmation, explain in the user's language:

- what changed,
- why it matters,
- what will behave differently,
- what remains unchanged,
- what is still uncertain,
- what the user needs to confirm.

Technical IDs are secondary traceability. **Never ask the user to approve an impact they cannot meaningfully evaluate.** Reframe, simplify, or give a scenario until the business meaning is answerable.

## 6. Minimum Revalidation

Do not reopen phases. Reopen only affected knowledge.

- Do not re-ask `AFFECTED_BUT_STILL_VALID` knowledge merely because it is connected.
- Revalidate `NEEDS_UPDATE` and `NEEDS_RECONFIRMATION` only.
- If new information extends an already-confirmed change, preserve confirmed understanding and revalidate only the delta.

## 7. Unrelated Findings

Record outside-frontier issues separately. Do not silently expand or block the active change unless the finding prevents reliable assessment of the current change.

**Discover broadly, change narrowly.**

## 8. Pending and Provisional Work

Pending truth is visible context, not approved truth.

If downstream work proceeds provisionally:

- make the dependency explicit,
- keep it traceable to the OPEN CHG,
- do not present it as approved truth,
- recheck only those dependents when the change resolves.

## 9. Final Confirmation

Show a plain-language summary:

`Before → After → downstream changes → unchanged areas → verified items → unresolved blockers`.

FINAL confirmation confirms business meaning, not machine integrity.

## 10. Commit

Before commit:

- `impact_confirmation: CONFIRMED`
- `final_confirmation: CONFIRMED`
- `blocking_status: CLEAR`

Build prospective current files only under:

`.ba/changes/.candidate/CHG-0001/`

Validate first:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/ba_change_commit.py" \
  --project "${CLAUDE_PROJECT_DIR}" \
  --change CHG-0001 \
  --candidate-dir "${CLAUDE_PROJECT_DIR}/.ba/changes/.candidate/CHG-0001"
```

Apply only after validation passes:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/ba_change_commit.py" \
  --project "${CLAUDE_PROJECT_DIR}" \
  --change CHG-0001 \
  --candidate-dir "${CLAUDE_PROJECT_DIR}/.ba/changes/.candidate/CHG-0001" \
  --apply
```

Do not manually mark `APPLIED`; the commit helper owns that state transition after exact readback and final lint.

## 11. Resume

Resume from the open CHG's status, unresolved material items, and Next Focus. Do not re-bootstrap discovery or ask resolved questions again unless new evidence contradicts them or the user's intent changes.
