# Brownfield Discovery

Use when an existing system, codebase, workflow, database, or documentation already exists.

1. Inspect README/docs, manifests, schemas, queries, workflows, tests, configuration, and recent implementation evidence relevant to the stated problem.
2. Distinguish **what the system currently does** from **what the business actually requires**.
3. Do not ask the stakeholder to restate facts visible in artifacts.
4. When code behavior conflicts with stakeholder intent, record the contradiction; do not assume implementation equals requirement.
5. Map only enough of the current system to understand the problem. Avoid unrelated reverse engineering.

Useful probes after inspection:
- Where does the real workflow deviate from the documented one?
- Which exceptions cause manual work or judgment?
- What decisions still require a human and why?
