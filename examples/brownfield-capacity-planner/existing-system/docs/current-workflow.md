# Current Workflow

1. ERP is the **source of truth** for production orders and available machine capacity.
2. A scheduled export feeds the existing planner utility every morning.
3. Planners review the generated CSV and manually decide which overloads to move.
4. The existing utility cannot explain why one order should move before another.

Known policy gap: the project documentation does not state which overload moves require manager confirmation. That must come from an authorized stakeholder rather than from code inspection.
