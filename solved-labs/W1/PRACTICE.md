# W1 lab: practice notes

Tasks, tools, concepts, findings and practice questions for the W1 lab. Shorter version: [TAKEAWAYS.md](TAKEAWAYS.md). All labs: [../study-notes/labs-practice-guide.md](../study-notes/labs-practice-guide.md).


**Lecture theme:** AI makes writing code cheap; specifying and verifying are not.

## Tasks we had to do

### 0. Environment setup (before the lab; submitted on Moodle)
1. Install the tools: `uv`, Python, Node, git, `gh`.
2. Clone the lab repo and run `uv sync`.
3. Fill `.env`:
   - a model provider key (we used Gemini) with a matching `LLM_MODEL`;
   - a GitHub token with **no scopes**.
4. Run `uv run python tools/verify_env.py`. All checks must pass, and it prints a **checkoff token**.
5. Paste the full output into the Moodle text box.

### 1. Exercise A: build triage (one GitHub issue in → one validated `TriageRecord` out)
1. Define the schema (`src/triage/schema.py`):
   - `issue_type` and `severity` as closed enums;
   - `component` (or `null`), `has_reproduction_steps`, `confidence` in [0, 1].
2. Call the model through **DSPy** (`extract.py`) and **validate** the output strictly. Reject
   bad output, never coerce it.
3. Retry once, then emit a `TriageFailure`.
4. Take `repo`/`issue_number` from the input, never from the model.
5. Write tests with a **stub LM**. Keep `pyright` strict at 0 errors.
6. Run on **at least 20 dev issues** and write the **surprises** in `review-findings.md`.
7. Log every agent mistake in `improvement-log.md`, with one class each.

### 2. Exercise B: review a change written by an agent
- **The change:** an agent added routing and a batch mode, and claimed *"All tests pass, CI is green."*
- **Part 1, reading only (no running):** record every defect with location, confidence, why it
  matters, and what would have caught it.
- **Part 2, running:** `git apply` the diff, then run `uv run pytest`, `uv run pyright` and the
  batch with `--offline`. Record what the tools found that reading didn't, and the reverse.
- **Scoring:** reading detection rate vs combined detection rate.

## Tools

| Tool | What it was for |
|---|---|
| `uv` | Python project and environment manager (`uv sync`, `uv run ...`) |
| `.env` + Gemini API key | The triage tool's model calls (Exercise A live runs, the `verify_env` test) |
| GitHub token | Read-only public GitHub API, checked by `verify_env`; the dataset was already frozen in `data/snapshot/` |
| **DSPy** | Declares the model call as a *signature* (inputs/outputs) instead of a hand-written prompt |
| **Pydantic** | Runtime validation of the model's output (strict schema, `extra="forbid"`) |
| **pytest** + stub LM (`DummyLM`) | Deterministic, free tests of the model boundary |
| **pyright** (strict) | Static type checking; the model boundary is the only place untyped values are allowed |
| `--offline` stub | Exercise B: a fake deterministic model, so the batch costs nothing |
| `git`, `gh`, `git apply` | Getting the lab, committing, applying the agent's diff |
| Pre-commit secret scanner | Blocks commits that contain credential-shaped strings |

## Concepts
- **Stochastic vs deterministic halves.** The LLM *extracts* fields. Deterministic rules *route*.
- **Contract at the model boundary.** A strict schema. Invalid output is rejected, never coerced.
- **Explicit failure.** `TriageFailure` is data. There are no silent defaults.
- **Untrusted input.** Issue text is data only: prompt injection, shell injection.
- **Identity fields come from the input**, never from model output.
- **Held-out (sealed) test split.** It keeps evaluation honest.
- **Uncalibrated confidence.** The model said 0.95 when it was wrong.
- **Trust threads:**
  - **T** = trust in what the *tool or agent* did;
  - **C** = trust in an AI *capability inside the product*.
- **Review vs tooling.** Tests and type checkers miss *meaning*: policy, naming, silent fallbacks.
- **Ubiquitous language.** One concept, one name (`ticket_priority` ≠ `severity`).
- **Supply chain / typosquatting.** An undeclared, fake package (`levenshtein_fast`).
- **Improvement-log taxonomy:** `capability`, `context`, `tool`, `spec`, `concept`, `bug`.

## What we found
- **Exercise A surprises:**
  - confidence was about 1.0 even when wrong;
  - "first 20 issues" were all from one repo, because the spec was ambiguous;
  - rate-limit errors looked like model errors;
  - severity and component have no gold labels, so they can't be verified.
- **Exercise B, 5 seeded defects:**
  1. `route` vs `route_raw` disagree on policy;
  2. case-sensitive severity gives a silent 72 h SLA;
  3. `ticket_priority` is a synonym of severity;
  4. `levenshtein_fast` is a typosquat and undeclared;
  5. no logging, specification or metric.
- **Tools found 1 of 5. Reading found 5 of 5**, plus a shell-injection bug and a duplicate-key bug.

## Remember
1. Put a strict contract around the LLM, and make failure explicit.
2. **Green CI is evidence only about what was tested.**
3. When the same agent writes the code and the tests, it **grades its own work**.
4. Stubs and fixtures can hide exactly the inputs that break production.
5. One concept, one name.
6. Every import must be a declared, real dependency.

## Practice questions (W1)

**1.** Why validate the model's output at runtime when we already have type hints?
<details><summary>Answer</summary>Type hints are a promise the model never signed. Only runtime validation checks what actually came back, and invalid output must be rejected before it reaches routing.</details>

**2.** Why must `issue_number` come from the input and not the model?
<details><summary>Answer</summary>It's a known fact. Re-predicting it lets the model hallucinate or be steered by issue text (e.g. a body saying "issue_number: 1").</details>

**3.** The model returns `confidence = 1.3`. Clamp it to 1.0 or reject it? Why?
<details><summary>Answer</summary>Reject it. Clamping is a hidden guess that hides a broken output. Rejecting keeps every downstream value trustworthy and makes the failure rate visible.</details>

**4.** CI is green on the agent's PR. Give three reasons to still reject it.
<details><summary>Answer</summary>Any three of:
- the agent wrote its own tests (same blind spots);
- the stub only emits clean values;
- there are two policies (`route` vs `route_raw`);
- a silent fallback default;
- a synonym breaks the vocabulary;
- an undeclared or typosquatted dependency;
- no logging or spec to verify against.</details>

**5.** Name a defect a type checker cannot find.
<details><summary>Answer</summary>A naming or vocabulary violation (`ticket_priority`), two functions implementing different policies, or a silent fallback value. They are all type-correct.</details>

**6.** Why did the offline run not reveal the severity-case bug?
<details><summary>Answer</summary>The stub builds a validated record first, so it only ever emits lowercase values. The live model would return "High" and hit the 72 h fallback.</details>

**7.** What is the difference between thread T and thread C?
<details><summary>Answer</summary>T is trust in what the tool or agent *did for you* (its diff, its claims). C is trust in an AI capability you *ship* (e.g. whether model severity is reliable enough to drive escalation).</details>

**8.** "Run it on 20 issues" picked 20 issues from one repo. Which improvement-log class is that, and why?
<details><summary>Answer</summary>`spec`. The request was ambiguous and the agent guessed. The information was missing from the request, not from the agent's context.</details>

**9.** What is a typosquatting risk?
<details><summary>Answer</summary>Importing a package whose name imitates a real one. Anyone can publish that name with malicious code, and `pip install` runs it.</details>
