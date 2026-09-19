# BA Discovery

[English](README.md) | [ไทย](README.th.md)

**Get the business right before you ask an agent to build the software.**

Coding agents are getting very good at turning a clear plan into working code. The harder problem is usually upstream: the problem is still fuzzy, the stakeholder and the agent mean different things, scope keeps moving, or the agent starts designing before anyone has agreed what success actually means.

BA Discovery is a small, composable set of Business Analysis skills for Claude Code. It helps you move from **background → goal → scope → requirements → system design → FRD**, while keeping the reasoning durable in the repo so another session or agent can pick it up without starting over.

It is intentionally **not** a coding workflow.

Once the business problem and the buildable intent are clear, hand the work to an engineering workflow. This README shows a recommended continuation using [mattpocock/skills](https://github.com/mattpocock/skills).

---

## Why Start Here?

A strong engineering workflow can build the wrong thing extremely well.

BA Discovery exists to reduce four failure modes that tend to happen **before** implementation starts.

### #1: The Agent Starts Solving Before It Understands

A user says, "we need a better planning system," and the agent immediately starts proposing architecture, databases, queues, or UI.

The missing step is understanding the current situation:

- Why does this project exist?
- What is painful today?
- What outcome actually matters?
- What is already true in the existing system?
- What is inside and outside the change?

BA Discovery starts there instead of treating the first idea as the requirement.

### #2: The User Gets Asked Questions They Cannot Meaningfully Answer

A technically correct question can still be a bad BA question.

A stakeholder may know the business extremely well while not knowing whether the solution should use event sourcing, MVVM, a graph database, or a particular integration pattern. Forcing them to choose creates fake certainty.

BA Discovery separates:

- what the stakeholder is the right source for,
- what can be learned from the codebase or documents,
- what should be researched,
- and what should be decided later by engineering.

The goal is not fewer conversations. The goal is **fewer redundant or unanswerable conversations**.

### #3: Requirements Drift Across Sessions

A long conversation is not durable project state.

BA Discovery keeps a lightweight **Project Brain** in the project being analysed:

```text
.ba/
├── PROJECT.md
├── REQUIREMENTS.md
├── DECISIONS.md
├── RESEARCH.md
└── phases/
```

The conversation can end. The project does not have to forget.

Approved phase snapshots preserve what was known at that point, while the canonical files continue to represent the latest valid truth.

### #4: A Good Spec Can Still Describe the Wrong Problem

Engineering specs are strongest when the decisions feeding them are already trustworthy.

BA Discovery focuses on the questions that come before implementation:

> Why are we doing this?
>
> What outcome are we trying to create?
>
> What exactly is in scope?
>
> What must the system do?
>
> Which rules and constraints are real?
>
> Which decisions are approved, and which are still assumptions?

That is the boundary this project owns.

---

## The BA Flow

You can run the whole flow or invoke one phase directly.

```text
Idea / Existing System
        │
        ▼
     /ask-ba
        │
        ▼
   /ba-discovery
        │
        ├── Understand
        │      Background
        │      Problem
        │      Goal
        │      Current state
        │
        ├── Requirements
        │      Needs
        │      Constraints
        │      Evidence
        │      Business rules
        │
        ├── Design
        │      System logic
        │      Boundaries
        │      Workflows
        │      Decisions
        │
        ├── Final FRD
        │
        └── Professional Report
```

The phases are independent skills, so you do not have to run everything in one session.

| Skill | Use it when |
|---|---|
| `ask-ba` | You are not sure where to start or which BA skill fits the situation |
| `ba-discovery` | You want the pipeline to guide you through multiple BA phases |
| `ba-understand` | The background, real problem, goal, or current state is still unclear |
| `ba-requirements` | You understand the problem and need to discover or validate what the system must do |
| `ba-design` | Requirements are sufficiently understood and you need the system logic and design |
| `ba-spec` | The decisions are settled and you want the consolidated Final FRD |
| `ba-report` | You want a professional, ELI5-style project report that non-technical readers can follow |
| `ba-change` | Approved truth may need to evolve, an OPEN change needs to resume, or new intent must be related to an existing pending change |

Phase prerequisites are **soft guards**, not prison bars. If you already have approved requirements from elsewhere, you can start at design. BA Discovery records the provenance instead of pretending an earlier BA phase happened.

---

## Question quality is part of the product

BA Discovery treats question design as a core behavior, not a tone preference. The shared **Question Contract** decides who should be asked, whether the answer can be found in artifacts or research instead, how much explanation is needed, and how the answer should be classified before it becomes durable truth.

- **Decision-critical** questions are asked one at a time so each answer can change the next question.
- Tightly related low-risk facts may be batched in groups of 2–4.
- A stakeholder is never asked to perform expert architecture reasoning they do not own.
- Casual estimates remain estimates until a hard requirement is actually confirmed.
- Progress is qualitative, not a fabricated percentage.

The practical rule is simple: **ask well, then preserve the answer honestly.**

## Project Brain roles

The Project Brain separates four kinds of information so summaries do not silently become competing truth:

- **CANONICAL** — current project truth such as problem, goal, scope, requirements, constraints, and decisions.
- **EVIDENCE** — research/source synthesis that informs decisions but does not become a requirement automatically.
- **DERIVED / NAVIGATION** — current phase, baselines, coverage, and Next Focus; these are projections, not a second source of truth.
- **HISTORICAL** — approved phase snapshots showing what was approved at a point in time.

Approved snapshots are append-only. Current truth may evolve, but history is not rewritten to make the project look cleaner.

## Change Management in v0.8

`/ba-change` is the single front door for evolving already-approved project truth without letting pending ideas contaminate the current baseline. BA Discovery remains **Single User Only**: the same interactive user provides business intent, clarification, impact confirmation, and final confirmation. Roles that exist inside the software being designed do not become additional BA participants.

The state model is intentionally simple:

- **Current canonical** — what is approved and true now.
- **Pending change** — durable working analysis in `.ba/changes/CHG-*.md`; visible when relevant, but not approved truth.
- **Applied change** — why current truth changed.
- **Phase snapshot** — what was approved at an earlier milestone.

Two operating rules keep AI context clean:

> **Stage the change, commit the truth.**
>
> **Current truth for work. History on demand.**

When new intent arrives, BA Discovery reads the actual OPEN change records first (**Read before relating**) and compares business intent before deciding whether to extend the same change or create a new one. Impact analysis follows causal evidence, not keyword similarity, and revalidates only knowledge that actually needs to change. Before canonical mutation, the user sees a final **Before → After** summary; deterministic tooling validates the prospective state, applies it, reads it back, and only then marks the change `APPLIED`.

Example: changing MOQ from one fixed threshold to Package-Size-dependent behavior can remain one change even when it includes no-MOQ exceptions, below-MOQ handling, or combining orders to satisfy MOQ, because those decisions collectively redefine the same business concern.

## `/ask-ba` can also tell you to leave BA

`/ask-ba` is not forced to recommend another BA phase. It may return one of three outcomes:

- **BA capability** — meaningful BA uncertainty remains.
- **Engineering workflow** — the business/specification boundary is sufficiently clear and the next work is implementation planning, coding, testing, review, or handoff.
- **No BA needed** — the request is already small, bounded, and sufficiently specified; more BA ceremony would not reduce meaningful uncertainty.

This keeps BA Discovery focused on its real job instead of trying to own the entire software lifecycle.

## Quick Start

Clone or download this repository, then load it as a Claude Code plugin:

```bash
claude --plugin-dir /path/to/ba-discovery
```

The canonical plugin commands are namespaced:

```text
/ba-discovery:ask-ba
/ba-discovery:ba-discovery
/ba-discovery:ba-understand
/ba-discovery:ba-requirements
/ba-discovery:ba-design
/ba-discovery:ba-spec
/ba-discovery:ba-report
/ba-discovery:ba-change
```

A simple first run:

```text
/ba-discovery:ask-ba
I have an existing planning system, but I am not sure whether I should start from the problem, the requirements, or the design.
```

Or let the pipeline guide the work:

```text
/ba-discovery:ba-discovery
Take this project through system design, but stop at each approval gate.
```

Or jump straight to one capability:

```text
/ba-discovery:ba-design
Use the approved requirements in docs/requirements.md as the design input.
```

Pause naturally. Resume naturally. The Project Brain is what carries the work forward.

---

## What BA Discovery Produces

The goal is not to generate as many documents as possible. The goal is to leave behind enough **approved, traceable project truth** that downstream agents do not have to reconstruct the reasoning from chat history.

Typical outputs include:

- project background, problem, and goal,
- scope and explicit non-goals,
- validated requirements and constraints,
- material decisions and their rationale,
- research findings with provenance,
- system logic and design,
- approved phase snapshots,
- a Final FRD,
- and an optional professional FRD report for business readers.

### The professional report

`ba-report` uses a fixed `BA-ELI5-FRD v1.0` pattern so reports remain familiar across projects:

1. Background
2. Goal
3. What We Will Do
4. Scope & Boundaries
5. Current → Future
6. Project / System Logic
7. Functional Requirements
8. Business Rules & Decision Logic
9. Data & Integrations
10. Roles, Responsibilities & Permissions
11. Exceptions & Edge Cases
12. Non-Functional Requirements
13. Acceptance & Success Criteria
14. Risks, Assumptions & Open Items
15. Technical Reference & Traceability

The report is a **presentation layer over approved project truth**. It must not invent missing requirements or silently resolve contradictions. HTML reports start from the fixed `skills/ba-report/assets/report-template.html` shell so typography, section layout, callouts, traceability, and print behavior stay consistent across projects.

---

## Optional Companion: ELI5

BA Discovery already has its own **Answerability Gate** and question-transformation rules. A stakeholder should not need a second skill just to understand the questions BA Discovery asks, and `ba-report` must remain able to produce its standard `BA-ELI5-FRD` report on its own.

So [DreambigOu/ELI5](https://github.com/DreambigOu/ELI5) is **recommended, but not required**.

Use it when the approved project truth needs to be re-explained for a specific audience:

```text
BA Discovery
Find and preserve the project truth
        │
        ├── /ba-report
        │   Standard professional project report
        │
        └── ELI5 (optional)
            Reframe an approved concept for a specific audience
```

Examples:

```text
Explain this architecture to a production manager.
Explain REQ-024 to a non-technical executive.
Explain why this project uses a graph database to a planner.
```

A useful boundary is:

> **BA Discovery finds and preserves the truth. ELI5 helps explain that truth to different people.**

Do not use ELI5 to silently change requirements, decisions, scope, or business rules. If an explanation exposes a real inconsistency or missing decision, route that discovery back through the appropriate BA phase first.

---

# Where BA Discovery Stops

BA Discovery is deliberately upstream of implementation.

Its job is to answer:

> **Are we building the right thing, for the right reason, inside the right boundary?**

Once the answer is stable enough, the job changes. Now you need engineering discipline: domain language, implementation seams, tickets, TDD, code review, and reliable handoff between coding sessions.

That is a natural point to continue with [mattpocock/skills](https://github.com/mattpocock/skills).

This repository does **not** bundle or copy Matt Pocock's skills. Install them separately and use whichever parts fit your engineering workflow.

---

# Continue With `mattpocock/skills`

Matt's repository is strongest on the engineering side of the boundary. Its current main build chain is:

```text
grill-with-docs
      ↓
   to-spec
      ↓
  to-tickets
      ↓
  implement
      ↓
 code-review
```

BA Discovery can feed that chain, but you do not always need every step.

## Recommended Routing After the FRD

### 1. Technical assumptions still need stress-testing

Use [`/grill-with-docs`](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs).

This is the best next step when the BA work is complete but the **engineering vocabulary, domain model, ADRs, or codebase-specific design** still need to be challenged against the real repository.

Think of the boundary like this:

```text
BA Discovery
Business truth + approved FRD
        │
        ▼
grill-with-docs
Technical/domain stress-test inside the codebase
```

Do not run it merely because an FRD exists. If the technical decisions are already settled, move on.

### 2. The decisions are settled and the build fits one session

Go directly to [`/implement`](https://github.com/mattpocock/skills/tree/main/skills/engineering/implement).

Matt's `implement` skill is intentionally downstream: it trusts the upstream plan and focuses on turning it into code with TDD, typechecking, tests, review, and a commit.

```text
BA Final FRD
    ↓
/implement
```

This is the shortest path when the change is small enough to fit in one fresh context window.

### 3. The decisions are settled but the build spans multiple sessions

Use [`/to-spec`](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-spec), then [`/to-tickets`](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-tickets), then `/implement` one ticket at a time.

```text
BA Final FRD
    ↓
/to-spec
    ↓
/to-tickets
    ↓
/implement   ← one tracer-bullet ticket per fresh session
    ↓
/code-review
```

`to-spec` is useful here because context windows end. It turns settled decisions into an engineering-facing spec. `to-tickets` then slices that spec into vertical, agent-ready units with explicit blocking edges.

### 4. The build is too large or uncertain for one planning session

Consider [`/wayfinder`](https://github.com/mattpocock/skills/tree/main/skills/engineering/wayfinder) before `to-spec`.

That is the heavier route for large engineering efforts where the technical path itself still needs to be resolved across multiple sessions.

### 5. You are changing agent, session, harness, or working directory

Use [`/handoff`](https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff).

This is particularly useful at the boundary between BA work and implementation, or whenever work moves to another agent.

A good handoff should **point at durable artifacts instead of copying the entire conversation**. For a BA Discovery project, useful pointers are usually:

```text
.ba/PROJECT.md
.ba/REQUIREMENTS.md
.ba/DECISIONS.md
latest approved phase snapshot
Final FRD
relevant engineering spec / ADRs
```

The receiving agent should start from the artifacts, not from a compressed retelling of every message that came before them.

### 6. You are not sure what Matt skill should come next

Use [`/ask-matt`](https://github.com/mattpocock/skills/tree/main/skills/engineering/ask-matt).

It is the router over Matt's user-invoked engineering skills, just as `/ask-ba` is the router over the BA workflow here.

---

## The Combined Workflow

The two repositories solve different layers of the same delivery problem.

```text
                         BUSINESS ANALYSIS

Idea / Pain / Existing System
            │
            ▼
        BA Discovery
            │
            ├── Background
            ├── Goal
            ├── Scope
            ├── Requirements
            ├── Decisions
            ├── System Design
            └── Final FRD
            │
            ▼
      "Are we building
       the right thing?"

──────────────────── ENGINEERING BOUNDARY ────────────────────

            │
            ▼
      mattpocock/skills
            │
            ├── grill-with-docs   optional technical stress-test
            ├── to-spec           preserve settled engineering intent
            ├── to-tickets        split multi-session work
            ├── implement         build with TDD
            ├── code-review       verify standards + spec
            └── handoff           cross agent/session boundaries
            │
            ▼
       Working Software
```

In one sentence:

> **BA Discovery helps you decide what should be built. `mattpocock/skills` helps you engineer and ship it well.**

They overlap just enough to form a useful seam, not enough that either needs to replace the other.

---

## Behavioral Confidence (v0.7)

BA Discovery now includes a vendor-neutral behavioral eval layer for the parts of BA quality that structural lint alone cannot prove. `scripts/ba_eval.py` evaluates normalized run records plus final `.ba/` state without calling any model API.

It is designed to catch or surface behaviors such as:

- asking the stakeholder for a fact that already exists in project evidence,
- turning uncertain language into confirmed truth,
- fabricating phase approval when entering Design from external approved requirements,
- re-bootstrapping Project Brain instead of resuming,
- and leaving answerability/question-pacing judgments for explicit semantic review instead of pretending they are deterministic.

The same scenario can be run with Claude Code, Codex, Gemini, or another AI by normalizing exposed events into the shared run-record schema. The core contract is **vendor-neutral**.

> **No vendor-specific feature is required for BA Discovery correctness.**

See [`evals/README.md`](evals/README.md) for manual capture, normalized events, result statuses, and optional adapter guidance. A complete **Brownfield** example is available at [`examples/brownfield-capacity-planner`](examples/brownfield-capacity-planner).


## Example: A Realistic Path

A [complete synthetic example](examples/order-allocation-planner) is included in this repository, with `.ba/` state, four approved snapshots, and a generated professional report.


You have an old planning application. Planners use SQL and Excel around it, and everyone already has an opinion about the replacement.

Start here:

```text
/ba-discovery:ba-discovery
Take us through the problem, requirements, and system design before we commit to a solution.
```

BA Discovery inspects what already exists, separates facts from assumptions, clarifies scope, and produces an approved FRD.

If the FRD says **what** the new planning capability must do, but the codebase still needs a sharper ubiquitous language and technical ADRs:

```text
/grill-with-docs
```

When the technical decisions are settled and the build is large:

```text
/to-spec
/to-tickets
```

Then start each implementation session from one ticket:

```text
/implement #123
```

If the next ticket will be picked up by a different agent or directory:

```text
/handoff
```

That is the intended relationship: **BA first, engineering second, durable artifacts at the boundary.**

---

## Design Principles

BA Discovery follows a few rules throughout the suite:

- **Accuracy over speed.** Important conclusions should be traceable to evidence.
- **Do not reinvent the wheel.** Research prior art before inventing a new framework or solution when existing knowledge can answer the question.
- **Ask the right source.** The stakeholder is one information source, not the default source for every question.
- **Make questions answerable.** Translate specialist choices into language and scenarios the stakeholder can meaningfully answer.
- **Conversation is not waste. Redundant conversation is waste.**
- **Do not fake completed phases.** External input is allowed; its provenance must remain visible.
- **Backtrack knowledge, not time.** If a later discovery invalidates an earlier assumption, preserve unaffected work and revalidate only the impacted frontier.
- **Project Brain is durable; the session is disposable.**

---

## Repository Layout

```text
ba-discovery/
├── .claude-plugin/
│   └── plugin.json
├── shared/
│   ├── contract-core.md
│   ├── contract-records.md
│   ├── contract-snapshots.md
│   └── question-contract.md
├── scripts/
│   ├── ba_lint.py
│   └── ba_eval.py
├── evals/
│   ├── behavior-contract.md
│   ├── schema/
│   ├── scenarios/
│   └── fixtures/
├── skills/
│   ├── ask-ba/
│   ├── ba-discovery/
│   ├── ba-understand/
│   ├── ba-requirements/
│   ├── ba-design/
│   ├── ba-spec/
│   └── ba-report/
├── examples/
│   ├── order-allocation-planner/
│   └── brownfield-capacity-planner/
├── tests/
├── CHANGELOG.md
├── VERSION
├── README.md
└── README.th.md
```

The `.ba/` Project Brain belongs to the project you are analysing, never to this plugin repository.

---

## Validate the Repository

```bash
python tests/validate_repo.py
```

---

## Credits & Related Work

BA Discovery is focused on Business Analysis and the pre-implementation boundary. It is designed to compose well with engineering workflows rather than own them.

For the engineering continuation described above, see:

- [mattpocock/skills](https://github.com/mattpocock/skills)
- [`grill-with-docs`](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs)
- [`to-spec`](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-spec)
- [`to-tickets`](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-tickets)
- [`implement`](https://github.com/mattpocock/skills/tree/main/skills/engineering/implement)
- [`handoff`](https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff)

Those skills are maintained in their own repository and are not included here.

## Structural integrity check (`ba-lint`)

BA Discovery remains clone-and-use. When Python 3 is available, the bundled `scripts/ba_lint.py` uses only the standard library to check deterministic `.ba/` structure such as duplicate IDs, dangling references, invalid lifecycle/phase values, missing baselines, snapshot naming, approval blocks, and bypass provenance. No `pip install` is required.

If Python 3 is unavailable, the conversational BA workflow still works, but **deterministic lint was not run** and the agent must not claim structural validation. `ba-lint` is structural validation, not a semantic score for whether a requirement is “good.”
