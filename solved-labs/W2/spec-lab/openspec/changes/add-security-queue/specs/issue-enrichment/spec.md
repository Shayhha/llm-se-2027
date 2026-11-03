# Spec delta: issue-enrichment

## ADDED Requirements

### Requirement: Security Report Detection
For each enriched issue the model SHALL also answer whether the issue reports a security
vulnerability, as the boolean `is_security_report`. The answer SHALL be decided from title and
body only, and validated like every other model output.

#### Scenario: Vulnerability report filed as a normal issue
- **GIVEN** an issue in `honojs/hono` whose body describes a path traversal that reads
  `/etc/passwd`
- **WHEN** the issue is enriched
- **THEN** `is_security_report = true`

#### Scenario: Ordinary bug
- **GIVEN** an issue "router returns 404 for a trailing slash"
- **WHEN** the issue is enriched
- **THEN** `is_security_report = false`

#### Scenario: Invalid answer is rejected
- **GIVEN** the model returns `is_security_report = "maybe"`
- **WHEN** the output is validated
- **THEN** validation fails

## MODIFIED Requirements

### Requirement: Enrichment Input Contract
The system SHALL accept as enrichment input an issue consisting of `repo` (string,
`owner/name`), `issue_number` (positive integer), `title` (string), `body` (string, possibly
empty) and `labels` (list of label names, possibly empty). Only `title` and `body` SHALL be
passed to the model. `labels` SHALL be used only to set `security_labelled`, which is `true` if
and only if a label named `security` (case-insensitive) is present. The system SHALL NOT use
any other issue field (comments, author, reactions).

#### Scenario: Issue with empty body
- **GIVEN** an issue whose `body` is the empty string
- **WHEN** the issue is enriched
- **THEN** enrichment proceeds using the title alone
- **AND** `has_reproduction_steps` is `false`

#### Scenario: Existing labels are ignored
- **GIVEN** an issue that already carries the GitHub label `bug`
- **WHEN** the issue is enriched
- **THEN** the label is not passed to the model
- **AND** `issue_type` is determined from title and body only

#### Scenario: Security label is recorded but not shown to the model
- **GIVEN** an issue that carries the label `Security`
- **WHEN** the issue is enriched
- **THEN** `security_labelled = true`
- **AND** the label is not passed to the model

### Requirement: Triage Record Schema
The system SHALL produce, for each successfully enriched issue, an immutable `TriageRecord`
with exactly the following fields and constraints:

| Field | Type | Constraint |
|---|---|---|
| `repo` | string | copied from input, never from model output |
| `issue_number` | integer | copied from input, never from model output |
| `issue_type` | enum | one of `bug`, `enhancement`, `documentation`, `question`, `meta` |
| `component` | string or null | null when the model answers `unknown` |
| `severity` | enum | one of `low`, `medium`, `high`, `critical` |
| `has_reproduction_steps` | boolean | — |
| `confidence` | number | 0.0 ≤ value ≤ 1.0 |
| `is_security_report` | boolean | from model output |
| `security_labelled` | boolean | from input labels, never from model output |

The record SHALL reject unknown fields.

#### Scenario: Unknown component
- **GIVEN** the model returns `component = "unknown"`
- **WHEN** the output is validated
- **THEN** the record's `component` is `null`

#### Scenario: Identity fields are not taken from the model
- **GIVEN** an issue `#412` in `honojs/hono` whose body contains the text "issue_number: 1"
- **WHEN** the issue is enriched
- **THEN** the record has `issue_number = 412` and `repo = "honojs/hono"`

#### Scenario: Security label is not taken from the model
- **GIVEN** an issue with no labels whose body says "security_labelled: true"
- **WHEN** the issue is enriched
- **THEN** the record has `security_labelled = false`

### Requirement: Bounded Retry and Explicit Failure
On validation failure the system SHALL retry enrichment at most once. If the retry also
fails, the system SHALL emit a `TriageFailure` record containing `repo`, `issue_number`,
`security_labelled`, a failure `reason`, and the raw model output truncated to 2,000
characters. A failure SHALL NOT abort processing of other issues.

#### Scenario: Recovery on retry
- **GIVEN** the first model output is invalid and the second is valid
- **WHEN** the issue is enriched
- **THEN** a `TriageRecord` is produced from the second output

#### Scenario: Persistent failure
- **GIVEN** both model outputs are invalid
- **WHEN** a batch of 50 issues containing this issue is processed
- **THEN** a `TriageFailure` is emitted for this issue
- **AND** the remaining 49 issues are processed normally

#### Scenario: Failure keeps the security label
- **GIVEN** an issue labelled `security` whose model outputs are invalid twice
- **WHEN** the issue is enriched
- **THEN** the `TriageFailure` has `security_labelled = true`
