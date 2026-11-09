# Labs practice guide (for quizzes and the final exam)

For each lab: **what we had to do**, the **tools** used, the **concepts** behind it, **what to
remember**, and **practice questions** with answers. Try each question before opening the answer.

---

# W1 lab: issue triage with an LLM, and reviewing an agent's change

**Lecture theme:** AI makes writing code cheap; specifying and verifying are not.
**Where:** [`../W1/`](../W1/) · summary in [`../W1/TAKEAWAYS.md`](../W1/TAKEAWAYS.md)

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

---

# W2 lab: specifications (SRS, user stories, OpenSpec, domain model)

**Lecture theme:** the software lifecycle and requirements. What changes when an AI agent writes the code.
**Where:** [`../W2/`](../W2/) · summary in [`../W2/TAKEAWAYS.md`](../W2/TAKEAWAYS.md)

## Tasks we had to do

### 0. Preparation (submitted on Moodle)
1. Install **OpenSpec ≥ 1.16** (`npm install -g @fission-ai/openspec@latest`, needs Node ≥ 22.12)
   and report `openspec --version`.
2. Read `W1/triage-spec-examples/`: the same feature as an OpenSpec change, an SRS, user stories and ADRs.
3. **Critique the flawed spec.** At least 15 problems in a table (problem, category, what the agent
   must guess and the risk), plus at least 3 missing requirement topics.
   - Categories: ambiguity, incompleteness, inconsistency, untestability, design-in-requirements,
     missing non-functional concern.

### 1. Setup before class
1. Copy `triage-spec-examples` to a working folder (`spec-lab`) and run `git init`.
2. Run `openspec init --tools none`.
3. Read the change request **CR-1**: security reports go to a private queue, are escalated, are
   handled within 24 h, are detected by the model, and the `security` label counts.

### 2. Cycle 1: SRS vs user stories (we were **Track B: user stories**)
- **B1:** rate US-06 and US-08 against INVEST, and name the weakest letter of each.
- **B2:** write CR-1 as stories in `docs/user-stories.md` (role, goal, benefit, Given/When/Then,
  size, traces to). Split it if it's too big, and update existing stories CR-1 makes false.
- **B3:** the agent test. List what a coding agent would still have to guess, and which stories interact.
- **Regroup:** compare with a Track A (SRS) partner. When would you choose each format?

### 3. Cycle 2: the OpenSpec workflow (everyone)
1. **C1:** run `openspec validate add-issue-triage --strict`. It fails, so fix the error (a missing
   scenario). Then `openspec archive add-issue-triage --yes`, and note what the main spec lost.
2. **C2:** run `openspec new change add-security-queue`. Write `proposal.md` and a delta spec per
   capability, using ADDED and MODIFIED requirements, each with at least one scenario.
3. **C3:** validate until it passes. Note one problem validate caught and one it can't catch.
   **Don't archive.**

### 4. Cycle 3: composing changes and the domain model (everyone)
1. **D1:** copy in two other teams' changes (priority score, component owners), then list and validate them.
2. **D2:** route records R1–R4 assuming all three changes are merged. Name the deciding requirement
   for each cell, or **?** where the specs contradict or depend on *when* routing runs.
3. **D3:** draft a **glossary** (one meaning per term) and **invariants** ("for every …, …") that
   would have prevented the conflicts, and say where to put them.

### 5. Submission
`worksheet.md` + `user-stories.md` (Track B) on Moodle.

## Tools

| Tool | What it was for |
|---|---|
| **OpenSpec CLI** | Spec-driven development: changes, delta specs, validation, archive |
| `openspec init` | Sets up `openspec/` in a project |
| `openspec list [--specs]` | Open changes, or the current main specs |
| `openspec show <id> [--json --deltas-only]` | Displays a change or spec (parsed deltas) |
| `openspec validate <id> --strict` | Checks structure: headers, every requirement has a scenario, MODIFIED blocks keep scenarios |
| `openspec new change <id>` | Creates an empty change folder |
| `openspec archive <id> --yes` | Merges a change's deltas into `openspec/specs/` |
| `/opsx:propose` | Asks a coding agent to draft a change (optional) |
| git | Its own history for `spec-lab`; `git diff --stat` shows what archive did |
| Node.js / npm | Needed to install OpenSpec |

## Concepts
- **SDLC with agents.** Humans own the ends: *specifying* and *verifying*. The spec is **executed**,
  so every gap becomes the agent's guess.
- **Need → requirement → design decision.** Functional requirement vs quality attribute vs constraint.
- **Formats:**
  - **SRS (ISO/IEC/IEEE 29148):** numbered IDs, priority, verification method, definitions, traceability.
  - **User stories:** role, goal and benefit, **INVEST**, **Given/When/Then** acceptance criteria.
  - **OpenSpec:** proposal (why), delta specs (ADDED/MODIFIED/REMOVED requirements with SHALL and
    scenarios), design, tasks.
- **29148 characteristics of a good requirement:** necessary, unambiguous, singular, feasible,
  verifiable, consistent, complete.
- **Traceability:** story ↔ requirement ↔ test.
- **Archive semantics.** Only requirements and scenarios reach the main spec. The rationale, design,
  open questions and quality targets stay behind in the archive.
- **A MODIFIED block replaces the whole requirement.** Copy it in full, then edit.
- **Composition of changes.** Changes that are each valid can contradict each other.
- **Domain model** (Domain-Driven Design): a **glossary** (ubiquitous language) plus **invariants**.
- **Deterministic routing.** It must be a pure function of the validated record: no clock, no live data.

## What we found
- **Prep:** 22 problems in the flawed spec, for example routing policy given to the model,
  contradictory rules, and labels leaking the answer.
- **Cycle 1:** CR-1 failed **S** in INVEST, so it was split into US-10, US-11 and US-12, and 5
  existing stories had to change. An agent would still have to guess 9 things.
- **Cycle 2:** the lecturer's example had a missing scenario. Our change validated with 2 ADDED and
  7 MODIFIED requirements.
  - **Validate caught** a deleted scenario.
  - **It missed** a wrong requirement name, and it can't judge policy at all.
- **Cycle 3:** all 3 changes validated, but every record R1–R4 had an undecidable cell:
  - a security bug could reach a public queue;
  - the SLA depends on 👍 counts at routing time;
  - `"Routing"` ≠ `router`;
  - a failure with a label has no SLA.
- **Experiment:** archive *refuses* a MODIFIED block that drops scenarios, but *accepts* one that
  silently drops a policy clause.

## Remember
1. **A valid spec isn't a correct spec.** Tools check form, people check meaning.
2. **Changes that are each valid can combine into an invalid system.**
3. **A MODIFIED requirement replaces the whole block.**
4. **One term, one meaning**, enforced by a domain model.
5. **Routing must be deterministic.** No live or time-varying inputs.
6. **Small requests hide big changes.**
7. Stories show *value and interactions*. An SRS or OpenSpec shows *precise, checkable rules*.
   Neither sees cross-change conflicts.

## Practice questions (W2)

**1.** What does INVEST stand for? Which letter did CR-1 fail as a single story?
<details><summary>Answer</summary>Independent, Negotiable, Valuable, Estimable, Small, Testable. It failed **S**: it changes routing, the model output and the input contract, so it was split into three stories.</details>

**2.** Why is US-08 ("hostile issue text is harmless") weakest on **T**?
<details><summary>Answer</summary>"Cannot steer routing" is a universal claim that no finite set of tests can prove, and "no process is started" has no defined way to check it.</details>

**3.** What does `openspec archive` keep in the main spec, and what does it drop?
<details><summary>Answer</summary>It keeps requirements and scenarios. It drops the proposal (why), the design and open questions, the tasks and the non-functional sections. The Purpose becomes "TBD".</details>

**4.** Give one thing `openspec validate` catches and one it can't.
<details><summary>Answer</summary>It catches a requirement with no scenario, or a MODIFIED block that drops existing scenarios. It can't catch wrong policy ("24 h cap or flat?"), contradictions between changes, or (as we observed) a MODIFIED header naming a non-existent requirement.</details>

**5.** Three changes all pass `validate --strict`. Why can the merged system still be wrong?
<details><summary>Answer</summary>Each is validated against today's spec, not against the others. One change silently removed the "unless overridden" clause that another depended on, and two changes MODIFY the same requirement.</details>

**6.** Why does a priority based on 👍 count break routing?
<details><summary>Answer</summary>👍 changes over time and isn't in the triage record. The same issue gets different SLAs depending on when it's routed, which violates "routing is a pure, deterministic function of the record". Reactions are also forbidden input.</details>

**7.** What is a domain model here, and how does it prevent these problems?
<details><summary>Answer</summary>A glossary (one definition per term) plus invariants ("for every issue, …"). New changes are checked against them. For example, I2 requires one precedence list for queues, and I4 says component is drawn from the owners vocabulary.</details>

**8.** Write a verifiable acceptance criterion for "security issues are handled within 24h max".
<details><summary>Answer</summary>"Given a security report with severity low, when routing runs, then sla_hours = 24. Given a security report with severity critical, then sla_hours = 4 (the 24 h is a cap)."</details>

**9.** Classify: "The model should output the queue and SLA as JSON."
<details><summary>Answer</summary>Design-in-requirements (it dictates the mechanism) and inconsistent with deterministic routing. It's also incomplete, because no schema is given.</details>

**10.** When would you choose an SRS over user stories?
<details><summary>Answer</summary>When you need auditability and complete coverage (numbered requirements, verification methods, traceability), e.g. for safety, security or contracts, or a spec an agent must implement without asking questions. Use stories for discussing value and scope and for iterative planning.</details>

---

# Across both labs

| Theme | W1 | W2 |
|---|---|---|
| Tools check form, not meaning | pytest 20/20 green, 4 of 5 defects missed | `validate` passes 3 conflicting changes |
| Vocabulary drift | `ticket_priority` vs `severity` | "critical", "priority", "component" with two meanings |
| Silent policy loss | `route_raw` drops two routing rules | a MODIFIED block drops the "unless overridden" clause |
| Determinism | the stub LM, temperature 0 and the cache | routing must not read live 👍 or late labels |
| Gaps get guessed | "first 20 issues" | 9 guesses in the agent test |
| Human role | review the diff against the spec | write the spec, glossary and invariants |
