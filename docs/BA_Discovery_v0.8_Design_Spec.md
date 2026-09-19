# BA Discovery v0.8 — Change Management Design Spec

**Status:** APPROVED
**Target:** v0.8
**Primary feature:** `/ba-change`
**Scope:** Design only — no implementation in this document
**Compatibility goal:** Vendor-neutral core behavior and durable artifacts

---

## 1. Background

BA Discovery already has a four-phase workflow:

1. **UNDERSTAND**
2. **REQUIREMENTS**
3. **DESIGN**
4. **SPEC**

It also has a durable Project Brain under `.ba/`, phase snapshots, approval provenance, behavioral evaluation, and deterministic linting.

The missing capability is what happens **after an approved project truth already exists and the user changes their mind, adds a new condition, or discovers that an approved assumption is no longer correct**.

Without an explicit change workflow, an AI can easily:

- silently overwrite approved meaning;
- treat a proposed change as if it were already approved;
- reopen too much work;
- ask the user to reconfirm things that are still valid;
- lose the reason why current truth changed;
- mix historical truth with current truth;
- misclassify a new statement as either a new change or part of an existing change;
- use conversation memory instead of re-reading authoritative project evidence.

v0.8 introduces `/ba-change` to handle these cases safely and with minimal user burden.

---

## 2. Core Goal

`/ba-change` shall let one user evolve an already-approved BA project while preserving:

- current approved truth;
- historical meaning;
- traceability;
- user comprehension;
- minimal revalidation;
- multi-session continuity;
- multi-AI portability.

The design must behave like a careful human BA:

> Receive the change → re-read the relevant truth → understand what changed → trace only the real impact → explain it in the user's language → revalidate only what is necessary → obtain final confirmation → verify integrity → commit the new truth.

---

## 3. Non-Negotiable Constraints

### 3.1 Single User Only

BA Discovery is a **single-user BA workflow**.

The same user is the only person who:

- provides business intent;
- clarifies meaning;
- confirms impact;
- confirms the final change;
- approves the resulting truth.

The workflow must not invent or require:

- stakeholder routing;
- multi-user consensus;
- approval chains;
- authority registries;
- manager approval;
- stakeholder matrices.

Roles that exist **inside the software being designed** may still be modeled when the user explicitly describes them. They are not participants in the BA workflow.

### 3.2 Vendor-Neutral Core

Correctness must not depend on Claude-, Codex-, Gemini-, or other vendor-specific context behavior.

Platform-specific adapters may exist later, but:

> Core behavior and durable artifacts must remain correct without them.

### 3.3 Human Meaning vs Machine Integrity

The user confirms **business meaning**.

Deterministic tooling verifies **state integrity**.

> **Human confirms meaning. Machine verifies integrity.**

---

## 4. Design Principles

### 4.1 Conversation Is Not Waste

> **Conversation is not waste. Redundant conversation is waste.**

The workflow may take multiple turns or sessions when that improves correctness.

The system must avoid repeating questions whose answers remain valid.

### 4.2 Time to Think Is Valid State

The user may pause at any approval point.

> **Time to think is a valid state, not an error or unfinished conversation.**

A pending change must be resumable without re-interviewing the user from the beginning.

### 4.3 Stage the Change, Commit the Truth

No proposed change may mutate approved canonical truth while analysis or revalidation is still in progress.

> **Stage the change, commit the truth.**

### 4.4 Backtrack Knowledge, Not Time

A change may affect knowledge that originated in an earlier BA phase, but the workflow does not “restart Phase 2” or “restart Phase 3”.

It reopens only the affected knowledge.

> **Do not reopen a phase. Reopen only the affected knowledge within that phase.**

### 4.5 Current Truth for Work, History on Demand

AI work should start from current approved truth plus relevant open changes.

Historical snapshots and applied changes are read only when needed.

> **Current truth for work. History on demand.**

### 4.6 Do Not Reason From Memory When Evidence Exists

Conversation memory can help navigation, but must not replace authoritative project evidence.

> **Memory helps navigation. Evidence supports decisions.**

Before impact assessment, the AI should re-read the relevant canonical records and, where necessary, linked project artifacts.

### 4.7 Discover Broadly, Change Narrowly

The AI may discover unrelated issues while investigating a change.

Those issues must not silently expand the current change.

> **Discover broadly, change narrowly.**

### 4.8 Comprehension Is a Gate

The user must understand what they are being asked to confirm.

> **Comprehension is a gate, not a writing style.**

Technical traceability may exist underneath, but confirmation must be expressed in the user's world.

### 4.9 Change Identity Follows Business Intent

A change is not defined by:

- individual requirement count;
- wording similarity;
- shared keywords;
- a shared implementation component;
- dependency alone.

> **Change identity is anchored by the business intent being changed.**

---

## 5. Project State Model

### 5.1 Canonical Current Truth

```text
.ba/
├── PROJECT.md
├── REQUIREMENTS.md
├── DECISIONS.md
├── RESEARCH.md
├── changes/
└── phases/
```

Canonical documents represent **current approved truth only**.

They must not contain obsolete truth merely because it is marked `SUPERSEDED`.

Example after a semantic change:

```text
DECISIONS.md

DEC-012
MOQ depends on Package Size
Derived from: CHG-0001
```

The obsolete record belongs in historical evidence, not ambient current context.

### 5.2 Open Change Staging

Each proposed or active change is stored durably:

```text
.ba/changes/CHG-0001.md
```

An open change is:

- durable;
- editable while analysis is in progress;
- visible to other BA skills when relevant;
- explicitly **not canonical truth**.

### 5.3 Historical Checkpoints

`phases/` remains immutable approved history.

A phase snapshot means:

> “This is what was approved at that milestone.”

It is not automatically updated after later changes.

### 5.4 Applied Changes

After a change is successfully applied, the change record becomes historical evidence explaining how current truth evolved.

An applied change is not part of the default working context unless needed for traceability or history.

---

## 6. Default AI Read Policy

### 6.1 Normal Work

Default working context:

```text
CURRENT CANONICAL
+
RELEVANT OPEN CHANGES
```

Do not load by default:

- all phase snapshots;
- all applied changes;
- all superseded records;
- unrelated open changes.

### 6.2 Historical Questions

If the user asks:

> “Why is this requirement like this now?”

Trace:

```text
Current record
→ Derived from CHG-xxxx
→ Read applied CHG
→ Read older baseline only if necessary
```

### 6.3 Key Rule

> **AI should not reconstruct present truth from history when present truth already exists.**

---

## 7. `/ba-change` Role

`/ba-change` is a **single front door** from initial change request through final confirmation.

The user should not need to manually switch between:

- `/ba-requirements`
- `/ba-design`
- `/ba-spec`

Internally, `/ba-change` may apply the same shared contracts and phase-owned rules, but phase routing is an implementation concern, not a user burden.

> **One change → one conversation → one front door.**

---

## 8. Change Lifecycle

```text
PROPOSED
   ↓
ANALYZING
   ↓
AWAITING_IMPACT_CONFIRMATION
   ↓
IMPACT_CONFIRMED
   ↓
REVALIDATING
   ↓
AWAITING_FINAL_CONFIRMATION
   ↓
APPLIED
```

Alternative terminal states:

```text
CANCELLED
SUPERSEDED
```

### 8.1 Meaning of Key States

**PROPOSED**
A change has been captured but analysis has not completed.

**ANALYZING**
The AI is understanding the delta, reading evidence, and tracing impact.

**AWAITING_IMPACT_CONFIRMATION**
The AI has an impact proposal and the user needs time or clarification before confirming it.

**IMPACT_CONFIRMED**
The user agrees that the AI understood the change and its impact correctly.

This does **not** mean the new truth is approved.

**REVALIDATING**
Only affected knowledge requiring update or reconfirmation is being resolved.

**AWAITING_FINAL_CONFIRMATION**
Revalidation is complete and the user is reviewing the final Before → After summary.

**APPLIED**
The user confirmed the final change, deterministic integrity checks passed, canonical truth was updated, and post-commit readback verified the result.

### 8.2 Important Distinction

```text
IMPACT_CONFIRMED
≠
CHANGE APPLIED
```

---

## 9. Change Record Structure

Example:

```markdown
# CHG-0001 — Change MOQ Behavior

Status: REVALIDATING

## What is changing?

Before:
Every order uses MOQ 5,000.

Proposed:
MOQ depends on Package Size and the system must handle orders that do not meet MOQ appropriately.

## Why are we changing this?

The real MOQ rule is not one fixed value.

## What is included?

- MOQ by Package Size
- Package Sizes with no MOQ
- MOQ source
- Below-MOQ evaluation
- handling of orders below MOQ

## What is not changing?

- Capacity logic
- Die availability
- PDD logic

## Change Identity

Business Concern:
MOQ

Change Intent:
Make MOQ handling context-dependent by Package Size.

Behavior Being Redefined:
- determine MOQ
- evaluate orders against MOQ
- handle below-MOQ orders

## Impact

Proposed Level:
PROPAGATING

Affected:
- DEC-006 → NEEDS_UPDATE
- AC-008 → NEEDS_UPDATE
- REQ-011 → AFFECTED_BUT_STILL_VALID

## Revalidation

Completed:
- MOQ source clarified
- below-MOQ behavior clarified

Open:
- none

## Candidate Truth

Before:
MOQ = 5,000

After:
MOQ determined by Package Size

## Final Confirmation

Status:
NOT_YET_CONFIRMED
```

### 9.1 Presentation Rule

> **Human-readable first, machine-traceable second.**

The user should not need to understand record IDs to understand or confirm the change.

---

## 10. Change Identity Review

When the user introduces a new intent while one or more changes are still open, the system must not automatically create another `CHG`.

### 10.1 Read Before Relating

The AI must:

1. identify currently open changes;
2. open and read their actual contents;
3. compare the new business intent against them;
4. decide whether the new intent belongs to an existing change.

Do not classify from:

- title alone;
- keyword overlap;
- semantic similarity alone;
- implementation component overlap.

> **Read before relating.**

### 10.2 Scope of Comparison

For identity classification, compare the new intent **only against currently open changes**.

Do not scan the entire project history.

Closed changes (`APPLIED`, `CANCELLED`, `SUPERSEDED`) are not part of the first-pass identity review.

### 10.3 Outcomes

```text
MATCH_EXISTING
NEW_CHANGE
UNCERTAIN
```

**MATCH_EXISTING**
Extend the existing change and re-evaluate only the impact delta.

**NEW_CHANGE**
Create a new `CHG-xxxx`.

**UNCERTAIN**
Ask one user-facing question about business intent.

Do not ask the user to classify the change record themselves.

### 10.4 Business Intent Anchor

A single change may contain multiple related decisions if they collectively redefine the same business concern.

Example:

```text
- MOQ varies by Package Size
- some Package Sizes have no MOQ
- the optimizer may combine orders to satisfy MOQ
```

These may belong to one change because they collectively redefine:

> “How should the system handle MOQ?”

### 10.5 Multiple Matches

If new intent appears to match more than one open change, the AI must not merge those changes automatically.

This is a signal that the existing change boundaries may overlap and requires user-visible clarification.

---

## 11. Delta Review for Existing Changes

If new information is classified `MATCH_EXISTING`, do not restart the change.

Instead:

```text
Existing confirmed understanding
+
New delta
→ Delta Impact Review
```

### 11.1 Possible Result

```text
NO_NEW_IMPACT
IMPACT_CHANGED
```

If no new impact exists, preserve previous confirmation.

If impact changed, show and reconfirm only the changed portion.

> **Preserve confirmed understanding; revalidate only the delta.**

If the new information invalidates part of prior understanding, invalidate only the affected confirmation, not the entire change.

---

## 12. Impact Analysis

### 12.1 Impact Levels

```text
NON_SEMANTIC
LOCAL
PROPAGATING
FOUNDATIONAL
IMPACT_UNKNOWN
```

**NON_SEMANTIC**
Wording, formatting, naming, or presentation changes with no business meaning change.

**LOCAL**
Business meaning changes but remains isolated.

**PROPAGATING**
One changed truth affects downstream requirements, decisions, acceptance criteria, design, or other dependent knowledge.

**FOUNDATIONAL**
The change alters a foundational problem, goal, scope, core workflow, or major business assumption.

**IMPACT_UNKNOWN**
Evidence is insufficient to classify reliably.

`IMPACT_UNKNOWN` is not a severity level. It means further inspection, research, or clarification is required.

### 12.2 AI Proposes; User Confirms

The impact level is an AI proposal supported by evidence.

Example:

> Proposed Impact: PROPAGATING
> The MOQ rule changes from one fixed threshold to Package-Size-dependent behavior. The lot validation and Below-MOQ behavior depend on the previous assumption. Project goal and capacity rules are unchanged.

The user confirms whether this business meaning is correct.

> **Impact level is proposed by AI, not declared as unquestionable truth.**

### 12.3 No Fake Precision

Do not produce:

```text
Impact Score: 7.4
Confidence: 83%
Similarity: 0.91
```

Use explicit evidence and reasoning instead.

---

## 13. Focused Evidence Traversal

Impact analysis must re-read real evidence instead of reasoning from memory.

The default traversal is:

```text
Read the change
      ↓
Read directly affected canonical truth
      ↓
Read what those records actually reference
      ↓
If causal dependency is found
      → follow it
      ↓
If no causal propagation remains
      → stop
```

### 13.1 Source Order

Evidence may include:

- current canonical Project Brain;
- linked project documentation;
- current code/schema/API where relevant;
- external research when required.

Code and documentation are evidence of current implementation reality.

They do not automatically redefine approved business truth.

### 13.2 Follow Evidence, Not Keywords

Search may locate candidate evidence.

A keyword match is not proof of impact.

> **Follow evidence, not keywords.**

### 13.3 Causal Link Test

For each candidate dependency, ask internally:

> If this change happens, can this item become incorrect, incomplete, require reinterpretation, or behave differently because of this change?

If yes, it enters the Impact Frontier.

If not, stop following that path.

### 13.4 Stop Rule

> **Read enough to establish or reject causal impact — then stop.**

This prevents every change from becoming a project-wide audit.

---

## 14. Impact Frontier

The Impact Frontier is the verified causal blast radius of the proposed change.

Each affected item may be classified as:

```text
AFFECTED_BUT_STILL_VALID
NEEDS_UPDATE
NEEDS_RECONFIRMATION
SUPERSEDED
```

Important:

> **Affected ≠ Invalid.**

A requirement may remain valid even if a supporting rule changes.

The Impact Frontier must also explicitly identify relevant items that remain unaffected where this helps the user understand scope.

---

## 15. Impact Comprehension Gate

Impact analysis is not complete until the user can meaningfully understand it.

Flow:

```text
Change
→ Understand Delta
→ Trace Impact
→ Build Internal Impact Map
→ Translate to User's Language
→ User Understands
→ User Confirms
→ Revalidate
```

### 15.1 Two-Layer Presentation

#### Human Layer

Explain:

- what changed;
- why it matters;
- what will behave differently;
- what remains unchanged;
- what remains uncertain;
- what the user needs to confirm.

#### Traceability Layer

May include:

- Change ID;
- affected record IDs;
- dependency path;
- effect classification;
- provenance;
- confirmation state.

### 15.2 Question Transformation

Do not ask technical questions merely because the underlying issue is technical.

Example:

Avoid:

> “Should MOQ mapping be persisted in a relational table or API?”

Prefer:

> “Where does the system currently get the MOQ for each Package Size — from existing data, a file, or a planning rule?”

Then the AI inspects the technical source itself.

### 15.3 Comprehension Loop

```text
Explain
   ↓
User meaning is clear?
   ├─ No → simplify / reframe / example
   │
   └─ Yes → Confirm
```

Do not rely solely on:

> “Do you understand?”

Use meaning-checking questions when necessary.

---

## 16. Impact Confirmation

Impact confirmation has three conceptual parts:

1. **Meaning Confirmation**
   Did the AI understand the proposed change correctly?

2. **Impact Confirmation**
   Does the user agree with what changes and what remains unchanged?

3. **Missing Knowledge Resolution**
   Resolve only material unknowns.

If the user expresses uncertainty such as:

> “I think so, but I'm not sure.”

Do not treat it as confirmation.

The change remains pending while the system helps make the issue answerable.

---

## 17. Revalidation Plan

After Impact Confirmation, `/ba-change` should show a short human-readable plan before asking further questions.

Example:

> After this MOQ change, three things need to be checked again:
>
> 1. where the MOQ for each Package Size comes from;
> 2. how the optimizer checks minimum quantity;
> 3. what happens when an order is below MOQ.
>
> Capacity, Die availability, PDD, and the overall project goal do not need to be reopened.

Technical IDs may appear underneath as reference only.

---

## 18. Minimum Revalidation

Revalidation is based on evidence, not ceremony.

```text
NON_SEMANTIC
→ verify that meaning truly did not change

LOCAL
→ revalidate changed truth and direct dependencies only

PROPAGATING
→ follow the verified Impact Frontier
→ revalidate only NEEDS_UPDATE / NEEDS_RECONFIRMATION

FOUNDATIONAL
→ return to the affected knowledge root
→ trace downward again
→ still do not restart all phases automatically

IMPACT_UNKNOWN
→ inspect / research / clarify first
```

Items marked:

```text
AFFECTED_BUT_STILL_VALID
```

must not be re-asked merely because they are connected.

> **Revalidation is selective by evidence, not ritual by phase.**

---

## 19. Unrelated Findings

During change analysis, the AI may discover a separate contradiction or issue.

If it is outside the causal Impact Frontier:

- do not expand the current change;
- record it as an Open Finding;
- tell the user briefly;
- do not block the current change.

Exception:

If the finding prevents reliable assessment of the current change, it becomes a blocking unknown for the current analysis.

> **A change owns only its causal impact frontier.**

---

## 20. Pending Change Visibility

A pending change must be visible context to other BA work, but it is not approved truth.

Example:

```text
Approved Truth:
MOQ = 5,000

Pending:
CHG-0001 proposes MOQ by Package Size
Status: REVALIDATING
```

If `/ask-ba` is asked about MOQ, it should communicate both states clearly.

> **Pending change is visible context, not approved truth.**

---

## 21. Provisional Work

New work may depend on an unresolved change.

It may proceed provisionally if the dependency is explicit.

Example:

```text
Design Candidate:
Optimizer groups orders before MOQ validation

Basis:
PROVISIONAL — depends on CHG-0001
```

Rules:

- never silently treat pending truth as approved;
- clearly disclose the provisional basis;
- preserve dependency back to the change;
- recheck the dependent artifact when the change resolves.

> **Approved truth drives committed work. Pending truth may drive provisional work, but never silently.**

---

## 22. Dependent Recheck

When a pending change resolves:

```text
Resolved CHG
   ↓
Find only items that explicitly depend on it
   ↓
Compare provisional basis vs final truth
   ↓
STILL_VALID
or
NEEDS_REVALIDATION
```

If final truth matches the provisional basis, the item can be promoted without repeating unnecessary discussion.

If the final truth differs, revalidate only the affected delta.

If the change is cancelled, all dependents based on its candidate truth must be rechecked.

> **Resolve the change, then reconcile only its dependents.**

---

## 23. Final Change Confirmation

After revalidation, the user receives a plain-language final summary:

```text
Before
After
What changed because of it
What remained unchanged
What was verified
Any unresolved material issue
```

Example:

> Before: Every order used MOQ 5,000.
> After: MOQ depends on Package Size.
> The optimizer's MOQ lookup and Below-MOQ behavior change.
> Capacity, Die availability, PDD, project goal, and project scope remain unchanged.
> No material issue remains unresolved.

The user confirms this business meaning before any canonical mutation.

---

## 24. Semantic History

Approved meaning must not be silently rewritten.

If business meaning changes:

```text
Old record
→ preserved in history

New current record
→ receives new identity
→ derived_from CHG-xxxx
```

Example:

```text
DEC-012
MOQ depends on Package Size

Derived from: CHG-0001
Supersedes: DEC-006
```

The old record is preserved in the applied change and/or historical phase snapshot.

Typographical or formatting edits that do not change meaning do not require semantic versioning.

> **Change history is append-oriented. Current truth advances; approved history is preserved.**

---

## 25. Pre-Commit Integrity Gate

Final user confirmation does not immediately mutate canonical truth.

Flow:

```text
Final User Confirmation
        ↓
Build Prospective Current Truth
        ↓
Deterministic Integrity Check
        ↓
PASS?
 ├─ No → canonical truth unchanged
 └─ Yes
        ↓
Commit canonical state
```

Checks should include at minimum:

- no candidate truth in canonical files;
- no obsolete/superseded truth in current canonical context;
- no conflicting active truths;
- new records created by a change contain provenance;
- supersession references are valid;
- open changes are not represented as approved truth;
- provisional dependencies are traceable;
- no unresolved blocking item exists for an applied change;
- current Project Brain passes `ba-lint`.

---

## 26. Post-Commit Readback

A successful file write is not sufficient.

After commit:

```text
Commit
   ↓
Read Current Canonical Again
   ↓
Compare actual state to confirmed Before → After
   ↓
PASS
   ↓
CHG = APPLIED
```

If readback does not match:

- do not mark the change `APPLIED`;
- treat the commit as incomplete;
- repair state before completion is claimed.

> **Write success ≠ Change success.**

---

## 27. Clean Canonical Rule

The current canonical files should contain only the current approved truth.

Do not keep obsolete meaning in normal working context merely with a `SUPERSEDED` status.

The historical truth remains available through:

- applied `CHG` records;
- phase snapshots;
- provenance links.

This intentionally reduces the chance that an LLM sees two incompatible truths in ambient context and reasons from the wrong one.

---

## 28. No Automatic Rebaseline in v0.8

v0.8 will not add an automatic `.ba/baselines/` layer.

Existing layers are sufficient:

```text
Current Canonical
= what is true now

Applied Change
= why current truth changed

Phase Snapshot
= what was approved at a meaningful earlier milestone
```

Creating extra baselines automatically would introduce additional copies of truth and increase ambiguity.

Explicit rebaseline/checkpoint behavior may be added in a future version when a real use case requires it.

---

## 29. Deterministic Context Selection

v0.8 should introduce a deterministic context-selection contract/helper concept.

Its purpose is not to create another source of truth.

Its purpose is to compute the appropriate read-set:

```text
Task
   ↓
Current canonical truth
+
Relevant open changes
   ↓
Minimal working context
```

Core requirements:

- historical content is not ambient by default;
- relevant open changes are visible;
- unrelated changes do not enter context merely because they exist;
- source selection should be reproducible across AI runtimes.

Possible implementation naming is intentionally deferred; the design contract matters more than the helper's CLI name.

---

## 30. User Experience Rules

The workflow should minimize process overhead.

The user should normally experience:

```text
Tell BA what changed
→ BA re-reads relevant truth
→ BA explains impact
→ user confirms understanding
→ BA asks only necessary follow-ups
→ BA shows final Before → After
→ user confirms
→ BA verifies and commits
```

The user should not need to understand:

- phase routing;
- record graph mechanics;
- supersession internals;
- dependency IDs;
- lint rules;
- state machine internals.

Technical traceability exists for reliability, not as a burden on the user.

---

## 31. Resuming Across Sessions

When `/ba-change` resumes:

1. read current canonical truth;
2. identify open change records;
3. read the focused change;
4. read its `Next Focus`, unresolved material questions, and current state;
5. continue from that point.

Do not re-ask already resolved questions unless:

- new evidence contradicts them;
- the user changed the intent;
- the answer is no longer sufficient for the current decision.

Example durable pause:

```text
CHG-0001
Status: AWAITING_IMPACT_CONFIRMATION

Next Focus:
Confirm the newly identified grouping impact.

Open:
Whether Package Size without MOQ should bypass grouping.
```

---

## 32. Multiple Open Changes

Multiple staged changes may exist simultaneously.

Only one change needs to be the primary focus of the current conversation.

When new intent arrives:

```text
Read open changes
→ Change Identity Review
→ MATCH_EXISTING / NEW_CHANGE / UNCERTAIN
```

Relations between distinct changes may later be represented where useful, but the AI must not automatically merge distinct open changes.

---

## 33. Behavioral Evaluation Additions

v0.8 should extend the v0.7 behavioral evaluation harness with scenarios covering at least:

### CM-01 — Extend Existing Change

An open MOQ change exists.
The user adds another MOQ-handling rule.

Expected:

- reads the active change;
- classifies `MATCH_EXISTING`;
- does not create a duplicate CHG;
- revalidates only impact delta.

### CM-02 — New Business Concern

An MOQ change is open.
The user changes Capacity behavior.

Expected:

- reads active change;
- classifies `NEW_CHANGE`;
- creates a separate change;
- does not merge based on shared optimizer component.

### CM-03 — Uncertain Change Identity

The new intent could plausibly belong to more than one open change.

Expected:

- does not auto-merge;
- asks one user-centered clarification question.

### CM-04 — Pending Truth Leakage

A change is pending.

Expected:

- current canonical remains unchanged;
- other BA work can see the pending change;
- candidate truth is not presented as approved truth.

### CM-05 — Minimum Revalidation

A propagating change affects three records but one remains valid.

Expected:

- valid record is not re-asked;
- only changed/uncertain items are revalidated.

### CM-06 — Historical Contamination

Current canonical contains new truth; older truth exists only in history.

Expected:

- normal work reads current truth;
- old snapshot is not loaded unless history is requested.

### CM-07 — Provisional Dependency

A design candidate depends on a pending change.

Expected:

- marks dependency provisional;
- does not silently promote;
- rechecks only the dependent when change resolves.

### CM-08 — Single-User Guard

The model attempts to invent another approver, stakeholder, manager, or authority.

Expected:

- behavioral evaluation fails.

### CM-09 — Post-Commit Verification

User confirms final change.

Expected:

- prospective state validated;
- canonical committed;
- canonical read back;
- only then marked `APPLIED`.

### CM-10 — Pause and Resume

User stops at an awaiting-confirmation state and resumes in a later session.

Expected:

- continues from durable state;
- does not restart questioning from the beginning.

---

## 34. Deterministic Validation Additions

`ba-lint` or an adjacent deterministic validator should eventually be able to detect:

- malformed change lifecycle states;
- `APPLIED` change with unresolved blocking items;
- missing `derived_from` on semantic replacement records;
- broken `supersedes` references;
- open change content leaked into canonical truth where detectable;
- unresolved provisional dependencies after their source change resolves;
- applied change missing final confirmation provenance;
- current canonical with known obsolete duplicate active truths;
- malformed change identifiers;
- invalid change-status transitions where deterministically observable.

Exact implementation details belong in the implementation plan, not this design spec.

---

## 35. Explicit Non-Goals for v0.8

v0.8 will not introduce:

- multi-user BA workflows;
- stakeholder/authority registries;
- approval hierarchies;
- opaque evidence grades;
- numeric impact/confidence scoring;
- full event sourcing;
- automatic rebaseline after every change;
- a new source-of-truth database;
- vendor-specific correctness dependencies;
- automatic project-wide audits for each change;
- automatic merging of overlapping changes;
- engineering handoff JSON as a maintained source of truth.

The derived engineering handoff artifact remains a possible later capability.

---

## 36. Relationship to Existing BA Skills

`/ba-change` becomes an additional user-facing capability, but it does not replace the four BA phases.

Its responsibility is:

> Safely evolve approved knowledge.

The four phases remain responsible for the semantics of their own knowledge domains.

The user does not need to route between them manually.

---

## 37. Core v0.8 Invariants

The following invariants define correctness:

1. **Single User Only.**
2. **Open change is durable but not canonical truth.**
3. **Canonical files represent current approved truth only.**
4. **Approved meaning is never silently rewritten.**
5. **Impact level is proposed by AI and confirmed by the user.**
6. **Impact must be explained in language the user can meaningfully evaluate.**
7. **AI re-reads authoritative evidence instead of relying on memory.**
8. **Impact traversal follows causal evidence, not keyword similarity.**
9. **Revalidation touches only what evidence says must be revisited.**
10. **Unrelated findings do not silently expand the active change.**
11. **New user intent is compared against actual open-change contents before creating a new CHG.**
12. **Confirmed understanding is preserved; only new delta is revalidated.**
13. **Pending truth may support provisional work only when explicitly marked and traceable.**
14. **Final user confirmation precedes mutation.**
15. **Deterministic integrity validation precedes canonical commit.**
16. **Post-commit readback precedes `APPLIED`.**
17. **History is queryable, not ambient context.**
18. **Correctness does not depend on one AI vendor's context behavior.**

---

## 38. End-to-End Workflow

```text
User expresses a change
        ↓
Read OPEN changes
        ↓
Change Identity Review
        ↓
MATCH_EXISTING / NEW_CHANGE / UNCERTAIN
        ↓
Create or update CHG staging
        ↓
Re-read relevant current truth
        ↓
Understand Before → Proposed
        ↓
Focused Evidence Traversal
        ↓
Impact Frontier
        ↓
AI proposes Impact Level + evidence
        ↓
Translate to user's language
        ↓
Impact Comprehension Gate
        ↓
User confirms impact
        ↓
Show Minimum Revalidation Plan
        ↓
Revalidate only necessary knowledge
        ↓
Final Before → After
        ↓
User final confirmation
        ↓
Build prospective current state
        ↓
Deterministic integrity validation
        ↓
Commit canonical truth
        ↓
Read canonical state back
        ↓
Verify against confirmed change
        ↓
Reconcile provisional dependents
        ↓
CHG = APPLIED
```

---

## 39. Design Summary

v0.8 treats change management as a controlled evolution of approved project truth rather than a rewrite of old documents.

The design deliberately separates:

```text
CURRENT CANONICAL
→ what is true now

OPEN CHANGE
→ what is being considered

APPLIED CHANGE
→ why truth changed

PHASE SNAPSHOT
→ what was approved at an earlier milestone
```

The AI is responsible for semantic work:

- understanding intent;
- identifying whether a new statement belongs to an existing change;
- tracing causal impact;
- explaining implications;
- asking answerable questions.

Deterministic tooling is responsible for structural safety:

- state validity;
- provenance;
- supersession integrity;
- commit checks;
- post-commit verification.

The resulting philosophy is:

> **Ask well → preserve truth well.**
> **Current truth for work. History on demand.**
> **Stage the change, commit the truth.**
> **Human confirms meaning. Machine verifies integrity.**
> **Do not make AI remember what it can read and verify.**
