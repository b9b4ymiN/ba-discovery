# BA Discovery Core Contract

This is the cross-cutting state contract for every mutating BA skill.

## Artifact roles

- **CANONICAL CURRENT** — latest approved project truth owned by `PROJECT.md`, `REQUIREMENTS.md`, and `DECISIONS.md` in their declared sections.
- **OPEN CHANGE** — durable candidate meaning in `.ba/changes/`; visible when relevant but **not canonical truth**.
- **EVIDENCE** — research/source synthesis in `RESEARCH.md`; it informs truth but does not become truth automatically.
- **DERIVED / NAVIGATION** — projections such as current phase, pipeline status, current baselines, coverage, and Next Focus. Rebuild these from canonical/history when needed.
- **HISTORICAL** — approved snapshots in `.ba/phases/` and `APPLIED` change records; append-only evidence of what was approved at that time.

One material fact has one canonical home. Derived summaries may point to it but must not compete with it.

## Current workflow vocabulary

Use only:

- `current_phase`: `UNDERSTAND` | `REQUIREMENTS` | `DESIGN` | `SPEC`
- `workflow_mode`: `DIRECT` | `PIPELINE`
- `target_phase`: `NONE` | `UNDERSTAND` | `REQUIREMENTS` | `DESIGN` | `SPEC`
- `pipeline_status`: `ACTIVE` | `PAUSED` | `COMPLETE`

Legacy v0.5.1 current-state values map lazily when touched:

- `BACKGROUND_DISCOVERY` → `UNDERSTAND`
- `REQUIREMENT_DISCOVERY` → `REQUIREMENTS`
- `SYSTEM_DESIGN` → `DESIGN`
- `FINAL_FRD` → `SPEC`

Do not rewrite historical approved snapshots merely to normalize old vocabulary.

## PROJECT.md roles

Canonical sections:

- Problem
- Goal
- Scope / Non-goals
- Current Understanding when it states current approved truth
- Assumptions
- Open Questions
- Needs Reconfirmation
- Current Risks

Derived / navigation sections or frontmatter:

- current_phase
- current_activity
- workflow_mode / target_phase / pipeline_status
- Current Baselines
- qualitative Coverage
- Next Focus

## Soft Guard

A missing preferred prior BA baseline is a risk, not an automatic lock. Recommend the safer prior phase. If the user explicitly proceeds with trustworthy external input, preserve provenance and validation status. Never fabricate a skipped phase, approval, or baseline.

## Pause / resume

On pause, persist only safe current truth, exact `current_activity`, pipeline status when applicable, and the smallest useful Next Focus. On resume, inspect durable state first; do not restart discovery or ask the user to repeat known context.

## Current truth and pending change

Default work reads current canonical truth plus relevant open changes. Historical state is loaded only when a trace/history question requires it. **Current truth for work. History on demand.**

For normal phase work, preserve the existing canonical-first write ordering. For change work, canonical mutation is governed by `shared/contract-changes.md`; do not use the normal phase write order to mutate canonical files incrementally.

Preserve unknown extensions unless explicitly superseded. Never invent approval, evidence, provenance, dates, or baseline validity.

## Deterministic validation policy

When Python 3 is available, run `${CLAUDE_PLUGIN_ROOT}/scripts/ba_lint.py --project ${CLAUDE_PROJECT_DIR}` on resume before trusting durable state, before presenting an approval-ready checkpoint, and before claiming final spec structural consistency. If Python is unavailable, state that deterministic lint was not run. Conversational BA work may continue, but never claim structural validation without command evidence.
