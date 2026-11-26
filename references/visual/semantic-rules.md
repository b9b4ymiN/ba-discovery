# Visual selection and semantic review

Start with the question the visual must answer. Use the selection matrix; never select a diagram just because its syntax is familiar.

| Intent | Primary kind | Semantic review |
|---|---|---|
| explain | text | Simple definition or already clear answer needs no visual. |
| process | flowchart | Actions, decisions, ordering and material exceptions; not a lifecycle. |
| responsibility | swimlane | Owners and handoffs; grouped flowchart, not unsupported swimlane syntax. |
| interaction | sequence | Participants, sender/receiver, message order, responses and failures; no invented interfaces. |
| boundary | architecture | Components, responsibility, system boundaries and dependency direction. |
| relationship | erd | Entities, evidence-backed cardinality; if unknown, omit the edge and explicitly ask or use text. Mermaid ER syntax requires cardinality: never fake it. |
| lifecycle | state | States, triggers, transitions and meaningful initial/end states. |
| condition | decision_table | Conditions, outcomes, conflict, exception and unknown rows. |
| alternatives | comparison | Same criteria across options; evidence and uncertainty; no invented scores. |
| current_future | before_after | Separate observed current behavior from candidate future; native table in Phase 02. |
| cause | cause_map | Grouped flowchart; evidence versus hypotheses, direction and unknowns. |
| impact | impact_graph | Dependencies, direction and evidence; no pending meaning promoted. |
| coverage | traceability | Actual IDs and links, gaps visible; never fabricate coverage. |
| screen | wireframe | Deferred to Phase 03; discuss screen goals, actions, states in text. |

## Complexity

L0: boundaries or overview. L1: logical workflow/components. L2: one focused detail. Prefer about 5–12 nodes or 3–7 table columns for first review, not hard completeness constraints. Split by decision, never discard exceptions just to meet a size target. Do not automatically generate all levels.

## Status

Split mixed evidence classes into separately labeled views. A renderer cannot certify the truth of edges, scope of approval or completeness. Review visually against source before presenting. If syntax is unsupported, use text or a suitable native table rather than inventing a successful render.
