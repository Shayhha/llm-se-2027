# Change: Route security reports to a private queue

*Author: Triage (CR-1)*

## Why

A vulnerability report against `honojs/hono` was filed as a normal issue. Triage sent it to the
public `engineering` queue, where it sat for three days before anyone noticed. Security reports
must reach a private queue and a human immediately, whatever type and severity the model gives
them.

## What Changes

- **ADDED** `Security Report Detection` (issue-enrichment): the model also answers whether the
  issue reports a security vulnerability (`is_security_report`).
- **MODIFIED** `Enrichment Input Contract` (issue-enrichment): the issue's labels are accepted as
  input, but are **never** passed to the model. They are used only to set `security_labelled`.
- **MODIFIED** `Triage Record Schema` and `Bounded Retry and Explicit Failure` (issue-enrichment):
  the record carries `is_security_report` and `security_labelled`, and a failure record carries
  `security_labelled`.
- **ADDED** `Security Queue` (issue-routing): a security report goes to the private `security`
  queue, is always escalated, and has an SLA of at most 24 hours.
- **MODIFIED** `SLA by Severity`, `Clarification Queue for Unreproducible Bugs`, `Escalation` and
  `Enrichment Failures are Routed` (issue-routing): security reports are an explicit exception
  to each.

## Capabilities

### New Capabilities
- (none)

### Modified Capabilities
- `issue-enrichment`
- `issue-routing`

## Impact

- Affected code: `src/triage/schema.py` (two new fields), `src/triage/extract.py` (new output
  field; labels read from the issue but kept out of the prompt), `src/triage/router.py`
  (new rule, evaluated first).
- New queue `security`. Making that queue private is an access-control setting outside triage.
- Evaluation: needs gold labels for security reports and a recall target (to agree with the
  triage lead).
- Out of scope: hiding, locking or relabelling the public GitHub issue itself.

## Open questions for the triage lead

1. Is "24h max" a cap (a critical report keeps 4 h) or a flat 24 h? This change assumes a cap.
2. Should a *question* about security ("is CSRF protection on by default?") go to `security`?
3. What recall and false-positive rate is acceptable for the model's detection?
