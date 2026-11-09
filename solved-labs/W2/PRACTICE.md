# W2 lab: practice notes

Tasks, tools, concepts, findings and practice questions for the W2 lab. Shorter version: [TAKEAWAYS.md](TAKEAWAYS.md). All labs: [../study-notes/labs-practice-guide.md](../study-notes/labs-practice-guide.md).


**Lecture theme:** the software lifecycle and requirements. What changes when an AI agent writes the code.

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
