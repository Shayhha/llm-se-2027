# Spec delta: issue-routing

## ADDED Requirements

### Requirement: Security Queue
A record is a **security report** if `is_security_report = true` or `security_labelled = true`.
A security report SHALL be routed to queue `security`, with `escalate = true` and a `reason`
naming the security rule. This rule SHALL take precedence over every other queue rule in this
spec (type-based queue, clarification queue, enrichment-failure queue). A `TriageFailure` with
`security_labelled = true` SHALL also be routed to `security`.

#### Scenario: Security bug report
- **GIVEN** a `bug` with `is_security_report = true`, `severity = medium`, reproduction steps
- **WHEN** routing runs
- **THEN** `queue = security`, `escalate = true`, `sla_hours = 24`
- **AND** `reason` names the security rule

#### Scenario: Security report without reproduction steps
- **GIVEN** a `bug` with `is_security_report = true` and `has_reproduction_steps = false`
- **WHEN** routing runs
- **THEN** `queue = security` (not `triage-clarify`)

#### Scenario: Label overrides the model
- **GIVEN** a record with `security_labelled = true` and `is_security_report = false`
- **WHEN** routing runs
- **THEN** `queue = security` and `escalate = true`

#### Scenario: Failed enrichment of a labelled issue
- **GIVEN** a `TriageFailure` with `security_labelled = true`
- **WHEN** routing runs
- **THEN** `queue = security`, `sla_hours = 24`, `escalate = true`

#### Scenario: Not a security report
- **GIVEN** a `bug` with reproduction steps, `is_security_report = false`,
  `security_labelled = false`
- **WHEN** routing runs
- **THEN** `queue = engineering`, as before this change

## MODIFIED Requirements

### Requirement: SLA by Severity
`sla_hours` SHALL be determined by `severity` alone, regardless of queue, except that the SLA
of a security report SHALL NOT exceed 24:

| `severity` | `sla_hours` | security report |
|---|---|---|
| `critical` | 4 | 4 |
| `high` | 24 | 24 |
| `medium` | 72 | 24 |
| `low` | 168 | 24 |

#### Scenario: SLA is unaffected by the clarify override
- **GIVEN** a `bug` with `severity = high` and `has_reproduction_steps = false`
- **WHEN** routing runs
- **THEN** `queue = triage-clarify` and `sla_hours = 24`

#### Scenario: Low-severity security report
- **GIVEN** a security report with `severity = low`
- **WHEN** routing runs
- **THEN** `sla_hours = 24`

#### Scenario: Critical security report keeps the shorter SLA
- **GIVEN** a security report with `severity = critical`
- **WHEN** routing runs
- **THEN** `sla_hours = 4`

### Requirement: Clarification Queue for Unreproducible Bugs
A record with `issue_type = bug` and `has_reproduction_steps = false` that is **not** a security
report SHALL be routed to `triage-clarify`, overriding the type-based queue.

#### Scenario: Bug without reproduction steps
- **GIVEN** a `bug` with `severity = medium`, `has_reproduction_steps = false`, not a security
  report
- **WHEN** routing runs
- **THEN** `queue = triage-clarify`, `escalate = false`
- **AND** `reason` mentions missing reproduction steps

### Requirement: Escalation
`escalate` SHALL be `true` if and only if at least one of the following holds:
1. `severity = critical`;
2. `severity = high` and `confidence < 0.6`;
3. the record is a security report.

Escalation SHALL apply regardless of the queue, including `triage-clarify`.

#### Scenario: Critical issue
- **GIVEN** a `question` with `severity = critical`, `confidence = 0.95`, not a security report
- **WHEN** routing runs
- **THEN** `escalate = true` and `queue = support`

#### Scenario: High severity, low confidence
- **GIVEN** a `bug` with reproduction steps, `severity = high`, `confidence = 0.59`
- **WHEN** routing runs
- **THEN** `escalate = true`

#### Scenario: Confidence threshold boundary
- **GIVEN** a `bug` with reproduction steps, `severity = high`, `confidence = 0.6`
- **WHEN** routing runs
- **THEN** `escalate = false`

#### Scenario: Critical bug without reproduction steps
- **GIVEN** a `bug` with `severity = critical`, `has_reproduction_steps = false`, not a
  security report
- **WHEN** routing runs
- **THEN** `queue = triage-clarify`, `sla_hours = 4`, `escalate = true`

#### Scenario: Low-severity security report is escalated
- **GIVEN** a security report with `severity = low`, `confidence = 0.95`
- **WHEN** routing runs
- **THEN** `escalate = true`

### Requirement: Enrichment Failures are Routed
A `TriageFailure` (see `issue-enrichment`) with `security_labelled = false` SHALL be routed to
queue `triage-manual` with `sla_hours = 72`, `escalate = false` and
`reason = "enrichment failed"`. A failure with `security_labelled = true` is routed by
`Security Queue`.

#### Scenario: Failed enrichment
- **GIVEN** a `TriageFailure` for issue `#88` with `security_labelled = false`
- **WHEN** routing runs
- **THEN** `queue = triage-manual`
