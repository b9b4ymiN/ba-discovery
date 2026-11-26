# BA Visual Contract v2 — Visual on Value

Visuals are derived communication artifacts, never canonical records, approval events, or a new workflow phase. Phase skills own reasoning, persistence and approval. The pipeline owns navigation. Existing core, question, snapshot and change contracts take precedence.

## Harness

1. Inspect legitimate evidence first. Classify the question the visual must answer, not keywords or the phase name. If concise text is sufficient, do not generate a file. Honor explicit opt-out.
2. When a visual is useful, load `assets/visual/selection-matrix.json` and select an intent and matching kind. Read `references/visual/semantic-rules.md` for the selected type. If multiple intents are intertwined, choose the decision-critical one first. Do not invent a renderer for an unsupported type.
3. Choose the smallest useful representation: L0 context, L1 logical, or L2 focused detail. Split large views only when useful. Check the diagram against evidence before rendering. Preserve exceptions and unknowns.
4. Separate OBSERVED, APPROVED, PROPOSED, ASSUMPTION, ILLUSTRATIVE views. APPROVED requires an actual approved snapshot, current canonical sources and verified approval scope; historical snapshot alone is not current truth. Open change dependencies are PROPOSED and traceable to CHG IDs. The assembler checks structure, not semantic correctness or actual approval scope.
5. Build transient v2 JSON as described in `docs/visual-foundation.md`; never put it in .ba/ or treat it as evidence. Include question, intent, kind, selection reason, level, status, references, source paths and open questions. Never include secrets. Use stable visual IDs only for the same decision/view.
6. Run `python "${CLAUDE_PLUGIN_ROOT}/scripts/ba_visual.py" --project "${CLAUDE_PROJECT_DIR}" --input <temporary-json>`. Add --update only for an existing v2 workspace in this project. Use remove_ids to remove obsolete views. Unchanged views retain original fingerprints; stale views remain visibly historical and must not be used as current evidence. Delete temporary input when feasible.
7. On resume, inspect Project Brain first; check freshness with --check before reusing workspace content. Fingerprints cover declared source bytes only. Missing evidence or rendering failure must not interrupt BA: continue in text, disclose the limitation, and never claim a render succeeded without verification. Do not silently install dependencies or contact remote services.
8. Present the workspace path, its decision/question, and the minimum next user question. Refresh manually. Approval remains in conversation; a visual is not an approval checkpoint, and absence of a visual cannot block one.

## Scope

Phase 02 integrates Understand, Requirements, and Design. Screen/wireframe rendering, dedicated change review and final report integration remain later work. The workspace is always DRAFT / NOT AN APPROVAL. Output remains one standalone offline HTML, no network requests, no arbitrary input HTML/JS, no approval action. Errors retain original diagram source. Existing report contract remains unchanged.
