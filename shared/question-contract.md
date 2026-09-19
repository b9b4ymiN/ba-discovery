# BA Discovery Question Contract

## Single User Only

The BA workflow has one interactive user. Project artifacts and external evidence may answer factual questions, but the workflow does not route clarification or approval to another human participant.

The BA is responsible for making questions answerable. Conversation is useful; redundant conversation is waste.

## Before asking

Run this checklist quietly:

1. **Is this needed now?** Do not ask merely because a template contains a field.
2. **Can evidence answer it?** Inspect project artifacts/current truth first; research external facts when appropriate.
3. **Does this require the user's business intent or confirmation?** Ask the single user only when the answer genuinely belongs to them.
4. **Can the user answer it meaningfully?** Calibrate only the concept needed for this decision.
5. **Will the answer materially change the next step?** If not, defer or omit it.
6. **Must wording be transformed into the user's world?** Preserve the decision distinction without specialist jargon.
7. **Is it decision-critical or a low-risk factual batch?** Choose pacing accordingly.

Unknown does not automatically mean “ask the user.”

## Question classes and pacing

### Decision-critical

The answer changes requirements, scope, authority, risk acceptance, or the next design branch. Ask **one at a time** so the answer can reshape the next question.

### Concept calibration

Use narrow, concept-specific, just-in-time calibration. Ask whether the user has used/decided this concept in practice or only knows it broadly. Do not infer broad expertise from role/title.

### Factual / low-risk

When several facts are tightly related and one answer will not change how the others should be asked, batch **2–4** items. Example: approximate user count, daily usage frequency, and whether night-shift use exists.

### Validation / confirmation

Group previously discussed statements into a compact confirmation set. Let the user correct only the inaccurate/open items rather than re-answering everything.

There is no global batch mode. Decision-critical questions remain adaptive.

## Never outsource expert reasoning

**Never outsource expert reasoning** to a user who does not own that decision.

Do not ask a non-architect to choose “event driven vs synchronous,” “graph vs relational,” or a framework merely because the BA needs an architecture answer. Ask for the business reality that drives the choice, then let the BA/researcher/architect derive the consequence.

Example:

- Bad: “Should processing be synchronous or asynchronous?”
- Better: “After the planner presses Optimize, must they wait on the screen for the result, or can the system accept the job and notify them later?”

## Explain enough, not a course

**Explain enough, not a course.** If a technical distinction must be understood, give the minimum explanation/example needed for a meaningful answer. Do not require the user to study a specialist domain before they can participate.

## Post-answer classification

Before promoting an answer to durable project truth, classify it as one of:

- observed fact,
- user statement,
- estimate,
- preference,
- need,
- constraint,
- decision-authority statement,
- assumption,
- uncertain signal,
- research finding,
- BA inference.

Promotion must preserve provenance and confidence. Casual wording is not automatically a requirement or decision.

Example: “น่าจะมีประมาณ 30 คน” is an **estimate (~30 users)**. It is not an exact constraint “system supports exactly 30 users.” Record the estimate if material; confirm a hard capacity only when that distinction affects the decision.

## Source + Answerability gates

A user question must satisfy:

- **Source Fit** — this person is a legitimate source for the requested information,
- **Comprehension Fit** — they can answer without learning a new specialist domain first,
- **Decision Fidelity** — simplification preserves the distinction that matters,
- **User-Effort Fit** — asking is necessary; the BA cannot reliably obtain it elsewhere.

If any gate fails, inspect, research, transform, or defer instead of asking the original question.

## Qualitative progress

When useful on a status request, pause/resume, or after a meaningful cluster, show qualitative coverage such as:

```text
Coverage
✓ Current workflow
✓ Problem
○ Constraints
○ Blind spots
```

Do not show this after every question. **Do not fabricate percentage completion.** Coverage is a navigation aid, not a completeness score.
