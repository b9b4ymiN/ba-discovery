# Changelog

## 0.8.0-rc1 — Change Management + Current Truth Integrity

- Added `/ba-change` as the eighth user-facing skill and single front door for evolving approved project truth.
- Added durable `.ba/changes/CHG-*` staging with explicit lifecycle, impact, confirmation, and post-commit verification state.
- Added business-intent-anchored Change Identity Review with read-before-relating behavior for open changes.
- Added focused causal Impact Frontier analysis, user-comprehensible impact confirmation, and Minimum Revalidation.
- Added clean-current-canonical rules so obsolete truth remains historical rather than ambient AI context.
- Added standard-library-only change-state, context-selection, and rollback-capable commit/readback helpers.
- Added explicit pending/provisional dependency behavior and dependent recheck.
- Added ten v0.8 behavioral regression scenarios including Single User Only and post-commit readback.
- Kept the core vendor-neutral; no `context: fork`, full event sourcing, automatic rebaseline, or multi-user approval workflow is required.

## 0.7.0-rc1 — Behavioral Confidence

- Added a vendor-neutral behavioral contract with stable criterion IDs for Source Routing, Answerability, Question Pacing, Answer Classification, Provenance, Approval Integrity, and Resume behavior.
- Added normalized run-record and expectation schemas so the same BA scenarios can be captured from Claude Code, Codex, Gemini, or another AI runtime without changing the core contract.
- Added standard-library-only `scripts/ba_eval.py`; it evaluates stored runs and final Project Brain state offline and never calls a model API.
- Added five behavioral scenarios: Greenfield Answerability, Brownfield Source Gate, External Design Bypass, Uncertain Estimate, and Resume Without Re-interview.
- Added intentional bad fixtures for Source Gate violations, fake approval, fake skipped-phase completion, uncertain-answer overpromotion, resume re-bootstrap, and structurally invalid final state.
- Added a complete `examples/brownfield-capacity-planner` project demonstrating inspection-before-questioning, source provenance, stakeholder-only authority questions, and existing-system constraints separated from future requirements.
- Added English/Thai documentation for manual multi-AI capture and optional adapters. No vendor-specific context/runtime feature is required for correctness.
- Kept the seven user-facing skills unchanged; `/ba-change`, `engineering-handoff.json`, Evidence Grade, and vendor-specific context isolation remain deferred.

## 0.6.0-rc1 — Question Quality + State Integrity

- Added a shared **Question Contract** covering Source Gate, Answerability Gate, decision-critical one-at-a-time pacing, low-risk 2–4 item factual batching, minimal concept calibration, and post-answer evidence classification.
- Unified current-state phase vocabulary to `UNDERSTAND`, `REQUIREMENTS`, `DESIGN`, and `SPEC`.
- Split Project Brain behavior into plugin-root shared contracts and removed `id_counters`; next IDs are derived from actual canonical records.
- Made CANONICAL / EVIDENCE / DERIVED / HISTORICAL artifact roles explicit.
- Added approval provenance and compact handoff requirements for v0.6+ approved snapshots without rewriting legacy history.
- Added standard-library-only `scripts/ba_lint.py` for deterministic structural checks; no `pip install` required.
- Added `/ask-ba` exits for **Engineering workflow** and **No BA needed** while keeping the navigator read-only.
- Added a fixed self-contained HTML shell for `/ba-report` so report presentation stays consistent across projects.
- Added a complete synthetic `examples/order-allocation-planner` project covering Project Brain, four approved snapshots, and a generated report.
- Kept deferred complexity out of this release: no Evidence Grade, `.ba/index.json`, `STAKEHOLDERS.md`, `/ba-change`, percentage progress, or cross-platform abstraction.


## 0.5.1-rc1 — Thai README and optional ELI5 companion

- Added a full `README.th.md` with the same product story, BA workflow, downstream engineering routing, and end-to-end examples as the English README.
- Added English/Thai language switching at the top of both README files.
- Added `DreambigOu/ELI5` as an optional companion for audience-specific re-explanation of approved project truth.
- Kept ELI5 explicitly optional: BA Discovery remains self-contained for stakeholder question transformation and professional `ba-report` generation.
- Clarified the responsibility boundary: BA Discovery finds and preserves project truth; ELI5 reframes that truth for different audiences; `mattpocock/skills` handles downstream engineering.

## 0.5.0-rc1 — Claude Code plugin packaging and BA-to-engineering handoff

- Repackaged the suite using Claude Code plugin layout with a root `skills/` directory and `.claude-plugin/plugin.json`.
- Rewrote the README around the core positioning: BA Discovery owns the Business Analysis boundary; engineering continues downstream.
- Added a practical continuation guide for `mattpocock/skills`, including `grill-with-docs`, `to-spec`, `to-tickets`, `implement`, `code-review`, `handoff`, and `ask-matt`.
- Documented when to skip or use each downstream engineering step instead of forcing one fixed pipeline.

## 0.4.0-rc1 — Professional ELI5 FRD reporting

- Added `/ba-report` as a seventh standalone Claude Code skill.
- Added fixed `BA-ELI5-FRD v1.0` report schema beginning with Background → Goal → What We Will Do → Scope & Boundaries.
- Added business-capability-first functional requirement presentation with Explain → Show → Specify layering.
- Added a self-contained, print-friendly HTML presentation contract with optional Markdown output.
- Kept `/ba-report` presentation-only: it cannot invent or mutate canonical project truth.
- Added navigator/pipeline handoff so the report can be recommended after an approved Final FRD without becoming a fifth BA phase.
- Extended static validation for report structure, traceability, and presentation contracts.

## 0.3.0-rc1 — Skill-only repository

- Repackaged BA Discovery as a standalone Claude Code skills repository.
- Removed packaged Python core/runtime dependency from the distribution.
- Added six project/add-dir skills: `ask-ba`, `ba-discovery`, `ba-understand`, `ba-requirements`, `ba-design`, and `ba-spec`.
- Added a shared prompt-level Project Brain persistence contract under `ba-discovery/references/`.
- Preserved phase-specific progressive references and pause/resume, soft-guard, provenance, snapshot, and handoff behavior.
- Added static repository validation.
