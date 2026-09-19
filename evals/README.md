# BA Discovery Behavioral Evals

v0.7 adds **Behavioral Confidence**: a vendor-neutral way to inspect whether an AI follows BA Discovery's behavioral contract instead of merely producing plausible prose.

The eval system has three layers:

1. `ba-lint` validates final Project Brain structure.
2. `ba_eval.py` evaluates deterministic behavior visible in a normalized run record plus final state.
3. Semantic criteria are left as explicit criterion-level review items rather than guessed by the script.

Possible criterion outcomes are `PASS`, `FAIL`, `NOT_OBSERVED`, and `NOT_APPLICABLE`. There is no aggregate Evidence Grade.

> **No vendor-specific feature is required for BA Discovery correctness.**

## Manual capture

Use this mode with any AI/runtime:

1. Start a fresh session or project using the scenario's seed and opening message.
2. Capture the `USER`, `ASSISTANT`, and any exposed `INSPECT`, `RESEARCH`, `STATE_WRITE`, or `APPROVAL` events.
3. Normalize those events to `evals/schema/run-record.schema.json`.
4. Preserve the final project directory when the scenario writes `.ba/` state.
5. Run the deterministic evaluator.
6. Review any semantic criteria using the prompt emitted in `semantic_review`.

Example:

```bash
python scripts/ba_eval.py \
  --scenario evals/scenarios/B01-brownfield-source-gate \
  --run evals/fixtures/good-runs/B01-inspects-first.json \
  --project evals/fixtures/projects/B01-good \
  --json-out /tmp/B01-result.json
```

Exit codes:

- `0` — no must-pass deterministic failure was observed.
- `1` — one or more must-pass criteria or final-state integrity checks failed.
- `2` — invocation/contract error.

A `0` does not mean every semantic criterion passed. Inspect the `semantic_review` section and all `NOT_OBSERVED` items.
The result also reports `must_pass_unobserved`; treat a non-zero value as missing evidence, not as a pass.

## Optional adapters

A Claude Code, Codex, Gemini, or other runtime adapter may automate log capture and normalization, but adapters are optional. They convert native logs into the same run-record format; they do not redefine the behavioral contract.

If a platform does not expose tool telemetry, omit the claim that telemetry is complete. Criteria that require unavailable telemetry become `NOT_OBSERVED` rather than an inferred pass or failure.

## Scenario set

- `G01-greenfield-answerability` — Answerability Gate and question pacing.
- `B01-brownfield-source-gate` — inspect retrievable project evidence before asking the stakeholder.
- `X01-external-design-bypass` — preserve external-input provenance without fake BA completion.
- `U01-uncertain-estimate` — keep an estimate uncertain instead of promoting it to confirmed truth.
- `R01-resume` — resume from durable Project Brain instead of re-interviewing the user.

## Writing a run record

Minimal example:

```json
{
  "scenario_id": "B01-brownfield-source-gate",
  "runtime": "your-runtime",
  "model": "optional free text",
  "telemetry": {"events_complete": true},
  "events": [
    {"type": "USER", "text": "ช่วยทำ BA ต่อจากระบบเดิมให้หน่อย"},
    {"type": "INSPECT", "target": "docs/current-workflow.md"},
    {"type": "ASSISTANT", "text": "..."}
  ]
}
```

Set `telemetry.events_complete` to `true` only when the capture really includes the event types needed by the criterion. Do not manufacture hidden tool events.
