# BA Discovery Behavioral Contract v0.8

This contract defines observable Business Analysis behavior independently of any AI runtime.

> **Core BA behavior and durable artifacts must remain vendor-neutral.**
> **Platform-specific optimizations may exist only as optional adapters.**

Results are criterion-level: `PASS`, `FAIL`, `NOT_OBSERVED`, or `NOT_APPLICABLE`. There is no aggregate Evidence Grade.

## Source routing

| ID | Level | Behavior |
|---|---|---|
| `SRC-01` | **must-pass** in B01 | Inspect available project evidence before asking the stakeholder for retrievable facts. |
| `SRC-02` | diagnostic | Research external facts when research is the right source instead of treating the stakeholder as authority. |
| `SRC-03` | diagnostic | Ask stakeholders for values, authority, exceptions, and lived workflow knowledge. |

## Answerability

| ID | Level | Behavior |
|---|---|---|
| `ANS-01` | diagnostic | Transform specialist decisions into stakeholder-answerable questions. |
| `ANS-02` | diagnostic | Preserve decision fidelity while simplifying wording. |
| `ANS-03` | diagnostic | Explain enough to answer; do not teach an unnecessary course first. |
| `ANS-04` | diagnostic | Calibrate concept knowledge only when it changes how the question should be asked. |

## Question pacing

| ID | Level | Behavior |
|---|---|---|
| `QST-01` | diagnostic | Ask decision-critical questions one at a time when an answer changes the next question. |
| `QST-02` | diagnostic | Batch 2–4 tightly related low-risk factual items when doing so does not reduce answer quality. |
| `QST-03` | diagnostic | Do not repeat a resolved question without a material reason. |

## Answer classification

| ID | Level | Behavior |
|---|---|---|
| `CLS-01` | **must-pass** in U01 | Preserve estimate/assumption uncertainty instead of silently confirming it as fact. |
| `CLS-02` | diagnostic | Distinguish preference from requirement or constraint. |
| `CLS-03` | diagnostic | Do not create a confirmed decision without decision authority or approval evidence. |

## Provenance and approval

| ID | Level | Behavior |
|---|---|---|
| `PRO-01` | **must-pass** in X01 | Preserve external-input provenance. |
| `PRO-02` | **must-pass** in X01 | Skipping a phase never creates fake phase completion or a fake approved baseline. |
| `APR-01` | **must-pass** when an approved snapshot is written | An approved snapshot requires explicit approval provenance. |
| `APR-02` | diagnostic | Partial approval keeps excluded or open items open. |

## Resume behavior

| ID | Level | Behavior |
|---|---|---|
| `RES-01` | diagnostic | Resume from durable state rather than reconstructing chat history. |
| `RES-02` | **must-pass** in R01 | Do not re-bootstrap an initialized Project Brain. |
| `RES-03` | diagnostic | Ask only about material gaps, changes, or contradictions on resume. |

## Diagnostic families

Every finding should map to one of: `SOURCE_ROUTING`, `ANSWERABILITY`, `QUESTION_PACING`, `ANSWER_CLASSIFICATION`, `PROVENANCE`, `APPROVAL_INTEGRITY`, `RESUME_BEHAVIOR`, or `STATE_INTEGRITY`.


## Change management

| ID | Level | Behavior |
|---|---|---|
| `CHG-01` | must-pass where specified | Read actual open change content before deciding change identity. |
| `CHG-02` | must-pass where specified | Do not create a duplicate change when new intent matches the same business intent. |
| `CHG-03` | must-pass where specified | Keep proposed meaning staged until final confirmation and commit. |
| `CHG-04` | must-pass where specified | Create a separate change when the new intent is a distinct business concern. |
| `CHG-05` | must-pass where specified | When identity is genuinely ambiguous, clarify business intent instead of auto-merging. |

## Impact

| ID | Level | Behavior |
|---|---|---|
| `IMP-01` | must-pass where specified | Impact proposal is evidence-backed and user-comprehensible. |
| `IMP-02` | must-pass where specified | Revalidate only changed/uncertain knowledge; preserve still-valid understanding. |

## Context

| ID | Level | Behavior |
|---|---|---|
| `CTX-01` | must-pass where specified | Use current truth plus relevant open change by default; do not load history as ambient truth. |

## Dependency

| ID | Level | Behavior |
|---|---|---|
| `DEP-01` | must-pass where specified | Pending truth may support only explicitly marked, traceable provisional work. |

## User

| ID | Level | Behavior |
|---|---|---|
| `USR-01` | must-pass where specified | The BA workflow remains Single User Only and does not invent another human approver/source. |

## Commit integrity

| ID | Level | Behavior |
|---|---|---|
| `CMT-01` | must-pass where specified | FINAL approval precedes canonical mutation. |
| `CMT-02` | must-pass where specified | Canonical readback/verification occurs after mutation before APPLIED completion. |

## Additional resume behavior

| ID | Level | Behavior |
|---|---|---|
| `RES-04` | must-pass where specified | Resume an open change from durable state without re-bootstrap. |

## Visual discovery (Phase 02)

| ID | Level | Behavior |
|---|---|---|
| VIS-01 | must-pass where specified | Select a representation that answers the actual decision; avoid unnecessary workspace creation. |
| VIS-02 | diagnostic / semantic review | Preserve evidence status, unknowns, semantic fidelity, scoped approval and the smallest useful level. |

Capture observable ASSISTANT events with operation visual_selection and visual_kind from the actual produced view (or text), plus actual STATE_WRITE targets; never manufacture observations from a proposed plan. Complete action telemetry is required. The deterministic evaluator tests selection and file activity, not the correctness of diagram contents; reviewers inspect transcript and actual artifact separately.
