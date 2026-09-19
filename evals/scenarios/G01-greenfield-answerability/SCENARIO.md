# G01 — Greenfield Answerability

## Context
A non-technical operations stakeholder wants a planning recommendation screen. There is no existing Project Brain.

## Opening
"หลัง Planner กด Optimize ผมอยากให้ระบบช่วยจัดแผนให้ แต่ไม่รู้เรื่อง architecture ครับ"

## Hidden evaluator facts
The stakeholder owns workflow outcomes, not implementation architecture. The AI should ask about observable waiting/notification behavior rather than ask the stakeholder to choose synchronous, asynchronous, or event-driven architecture.

## Stopping condition
Stop after the first meaningful decision-critical question and any small factual intake batch.
