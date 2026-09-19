# BA Professional ELI5 FRD Report Pattern

**Pattern name:** `BA-ELI5-FRD v1.0`

This is the fixed content schema for `/ba-report`. The order is locked so reports are comparable across projects. Content depth adapts to the project; heading order does not.

## Core narrative

The reader should always be able to follow this chain:

```text
Why does this project exist?
        ↓
Where are we going?
        ↓
What will we do?
        ↓
Where does the responsibility stop?
        ↓
What changes from today?
        ↓
How does the project/system actually work?
        ↓
What must each capability do?
        ↓
What rules, data, roles, exceptions, and quality expectations control it?
        ↓
How will we know it works?
```

## Fixed section order

### 1. Background

Purpose: explain the current situation and why this project exists.

Include when supported by approved truth:

- business/project context,
- current problem or opportunity,
- why the current state is insufficient,
- important history that explains the project,
- why action is needed now (only if evidenced).

Do not start with features. Give the reader the reason for the project first.

### 2. Goal

Purpose: state where the project intends to go.

Include:

- desired outcomes,
- business/user value,
- what success should feel/look like,
- measurable targets only when approved/evidenced.

Goals are outcomes, not a feature list.

### 3. What We Will Do

Purpose: explain the change being introduced in one coherent solution story.

Include:

- solution concept,
- major capabilities,
- the relationship between those capabilities and the Goal,
- what the project changes at a high level.

Avoid detailed implementation architecture here.

### 4. Scope & Boundaries

Purpose: make BA ownership/boundaries explicit before describing future flows.

Use this fixed subsection pattern:

#### 4.1 In Scope
What this project is responsible for delivering/changing.

#### 4.2 Out of Scope
Related things that this project explicitly will not deliver/change.

#### 4.3 System / Process Boundary
Where responsibility starts and ends.

#### 4.4 External Responsibilities
Responsibilities owned by other systems, teams, vendors, or people.

#### 4.5 Non-Goals
Things that may sound related but are explicitly not objectives of this project.

### 5. Current → Future

Purpose: let the reader see the change before reading detailed rules.

Show:

- current workflow/state,
- key current pain points,
- future workflow/state,
- exactly what changes,
- what intentionally remains unchanged.

Prefer a side-by-side Current vs Future table or before/after flow when useful.

### 6. Project / System Logic

Purpose: explain the end-to-end logic of the project in plain language.

Cover the main sequence:

```text
Input / Trigger
    ↓
Main processing / workflow
    ↓
Decision points / business rules
    ↓
Human/system responsibility
    ↓
Output / Result
```

Include meaningful branch points and ownership. Keep this implementation-neutral unless a technical choice is already approved and materially affects behavior.

### 7. Functional Requirements

Purpose: explain what the solution must do in a way business readers can follow and engineers/AI can trace.

Group by **business capability or user goal**, never by implementation component.

Every functional area uses this exact pattern:

#### 7.x [Business Capability / User Goal]

**Purpose**
Why this capability exists.

**When It Happens**
Trigger, actor, precondition, or situation that starts the behavior.

**How It Works**
A clear step-by-step functional flow.

**Business Rules**
Rules/conditions that affect the result. Reference `REQ-*` / `DEC-*` where applicable.

**Example**
A realistic scenario showing the behavior.

**Exceptions**
Important deviations, invalid conditions, overrides, or alternate paths.

**Expected Result**
What the user/business/system should have at the end.

**Traceability**
Relevant canonical IDs such as `REQ-0001`, `DEC-0001`, constraints, and acceptance references.

### 8. Business Rules & Decision Logic

Purpose: collect cross-functional rules that determine behavior or outcomes.

For each material rule explain:

- rule in plain language,
- reason/rationale when known,
- condition,
- expected behavior,
- exception/override,
- authority when a human decision is required,
- canonical references (`REQ-*`, `DEC-*`, etc.).

Do not duplicate every rule from Section 7; use this section for rules that deserve a consolidated view or affect multiple capabilities.

### 9. Data & Integrations

Purpose: explain what information enters/leaves the project and why.

Cover:

- important data concepts,
- source of truth / ownership,
- source → use → destination,
- external systems/interfaces,
- timing/direction of exchanges,
- approved validation/quality rules,
- privacy/security constraints when approved.

Explain business meaning before schemas/field names.

### 10. Roles, Responsibilities & Permissions

Purpose: make human/system authority explicit.

Cover:

- who does what,
- who can view/change/approve/override,
- where system automation ends and human authority begins,
- separation of duties when relevant.

### 11. Exceptions & Edge Cases

Purpose: show what happens when the happy path is not true.

Cover material cases such as:

- missing/invalid input,
- conflicting rules,
- unavailable external systems,
- rejected approvals,
- partial completion,
- manual override,
- retry/recovery expectations,
- known unresolved edge cases.

### 12. Non-Functional Requirements

Purpose: explain how well the solution must operate, not what feature it performs.

Include only applicable confirmed expectations, such as:

- performance,
- security,
- privacy,
- reliability/availability,
- auditability,
- scalability,
- usability/accessibility,
- maintainability/supportability,
- compliance.

Use measurable/verification-friendly wording when the source supports it. Do not invent target numbers.

### 13. Acceptance & Success Criteria

Purpose: explain how stakeholders will know the project/functionality is acceptable.

Separate when useful:

- project success outcomes,
- functional acceptance conditions,
- business/UAT scenarios,
- technical verification expectations.

Trace material criteria back to `REQ-*`, decisions, or approved goals.

### 14. Risks, Assumptions & Open Items

Purpose: keep uncertainty visible rather than hiding it in prose.

Separate:

- Risks,
- Assumptions,
- Open Questions / Decisions,
- Dependencies,
- items needing reconfirmation.

Do not present an assumption as confirmed truth.

### 15. Technical Reference & Traceability

Purpose: give engineers, reviewers, auditors, and AI a precise path back to approved truth without making the main report read like a database dump.

Include as applicable:

- Requirement traceability (`REQ-*`, `CON-*`, `NEED-*`),
- Decision traceability (`DEC-*`),
- final baseline references,
- requirement → design → acceptance mapping,
- approved high-level architecture/components,
- external interface references,
- source documents/research references,
- still-open implementation decisions.

This is the appendix/detail layer. It must not contradict the plain-language sections above.

## Explain → Show → Specify

Use this pattern within sections when it improves understanding:

**Explain** — plain language, purpose, meaning.
**Show** — scenario, example, flow, comparison, or table.
**Specify** — exact rules, IDs, acceptance criteria, interfaces, constraints.

A non-technical reader should be able to stop after Explain/Show and still understand the project. An engineer/AI should be able to continue into Specify and recover precise traceability.

## Consistency rules

1. Keep all 15 headings in this order for every report.
2. If a section is not applicable, state **Not applicable in the current approved scope** and briefly explain why when useful.
3. Never add a requirement, decision, metric, integration, role, or exception solely to make the report feel complete.
4. Never hide unresolved assumptions/open items.
5. Summaries are presentation only; `.ba/` remains canonical truth.
6. Prefer business language first; define unavoidable jargon at first use.
7. Use examples to clarify logic, but label illustrative examples when they are not approved business data.
