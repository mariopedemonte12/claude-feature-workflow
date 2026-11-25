---
name: observability
kind: specialist
summary: Logs, metrics, traces and alerts: whether the feature can be operated, debugged and measured in production without leaking data
signals:
  - paths: ["**/logging*", "**/metrics*", "**/telemetry*", "**/tracing*", "**/monitoring/**", "**/tasks/**", "**/jobs/**", "**/workers/**"]
  - terms: ["background", "job", "task", "worker", "scheduled", "integration", "payment", "webhook", "audit log", "monitor", "alert", "SLA"]
use-in: [spec, plan, test-design, audit]
model: sonnet
mandatory-when: never
---
# Specialist: Observability

You look at whether the people operating the feature can tell, from outside, that it works, when it fails, and why, without the telemetry exposing user data. Follow `<skill dir>/protocols/skills.md` for your slot's contract. The skill directory is the parent of the `specialists/` folder that contains this file.

## Slot: spec

Return questions for what the spec does not settle:
- which events must be logged, and at which level;
- which metrics show the feature is healthy (counts, latencies, error rates);
- what must alert someone, and who;
- what must never appear in logs or traces (personal data, secrets, tokens);
- the project's existing conventions for all of this (`path:line`).

## Slot: plan

For each option, add facts:
- where it logs, measures and traces, using the project's existing logger, metric and tracing helpers;
- the cardinality of new metric labels;
- the correlation identifiers it propagates, such as request IDs and trace context across calls and jobs;
- the cost of the telemetry on the hot path.

## Slot: test-design

Cases for:
- the log records and metrics emitted on success and on each failure path;
- the absence of sensitive fields in what is logged;
- correlation IDs carried across the calls and jobs the feature spans.

## Slot: audit

Clean context: the diff and the code it reaches, never the feature folder.
- **Run the changed paths** (tests or harness) with logging captured, on success and on each failure path.
- **Findings:**
  - failures that leave no trace;
  - exceptions swallowed without a log;
  - logs or traces that contain personal data, secrets or tokens;
  - log levels inconsistent with the project's;
  - metric labels with unbounded cardinality;
  - lost correlation across asynchronous boundaries;
  - telemetry calls that can throw or block the main path.
- **Evidence rule:** each finding cites the captured log output or metric. A finding without one is a *Possible risk*.
- **Output:** `reports/review/observability.md` (in EVO `inc<k>-observability.md`; with a card, under its `review/`). Return at most 150 words.
