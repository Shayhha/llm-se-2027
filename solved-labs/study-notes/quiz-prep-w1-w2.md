# Quiz prep: W1-W2

## How to use this

1. Read the **summary** (section 2).
2. Answer **set A** and **set B** out loud *without* looking.
3. Check against the **answer keys** at the end, and reread what you got wrong in the reading book.

The quiz is 5–10 minutes, handwritten, conceptual, and covers the previous week's lecture.

### Most likely topics

If you only have 10 minutes, know these four:
1. The **4 broken assumptions**.
2. The **new artifact per SDLC stage**: spec, agent context, provenance, independent tests, gates, drift checks.
3. **Need / requirement / design decision** and **FR / QA / constraint** classification.
4. **Rewriting a vague requirement into a verifiable one.**

## W2 one-page summary

### 1. Methodology and SDLC (slides 40–41)

A **methodology** is a shared way of organising the work: *which activities, in what order, by whom, which artifacts, how quality is checked.*

| Stage | Main output (traditional) |
| --- | --- |
| Plan | requirements spec, user stories, acceptance criteria |
| Design | architecture, ADRs, API contracts, data model, platform |
| Build | codebase, build config |
| Test | test suites, deterministic pass/fail, coverage |
| Deploy | CI/CD, infrastructure as code, releases |
| Maintain | fixes, patches, monitoring, runbooks, postmortems |

### 2. The four hidden assumptions that AI breaks (slide 42) ⭐

1. **Coding is expensive.** Now code is cheap.
2. **Code is the source of truth.** Now the *spec* must be.
3. **Behaviour is deterministic, so a test oracle exists.** An LLM in the product is not deterministic.
4. **Dependencies change only when we upgrade them.** The AI supplier changes models under you.

### 3. SDLC with coding agents (slides 43–50) ⭐

Same stages, but **humans own the two ends: specifying and verifying.**
The question at every stage: *what must a person own so we can trust what the agent produces?*

| Stage | New artifact with agents | One-line why |
| --- | --- | --- |
| Plan | **Executable spec** (acceptance criteria, task breakdowns) | Gaps in the spec get filled by the agent's *guesses* |
| Design | **Agent context**: rules files, skills, **tool permissions** | Design now constrains two builders: the product *and* the agent |
| Build | **Provenance**: agent sessions, PRs with review records | Code is cheap; **review becomes the bottleneck** |
| Test | **Independent acceptance tests** from the spec, human-owned | Otherwise the agent **grades its own work** |
| Deploy | **Approval gates**, agent permission policy | Deploy is a **trust boundary** |
| Maintain | **Spec-first changes**, spec–code **drift checks** | Change the spec, then regenerate or amend the code |

### 4. Second shift: AI *inside* the product (slides 51–52)

The component is **non-deterministic**, the interface is **natural language**, and the **supplier keeps changing**. So:
- **Plan:** behavioural targets (quality *rates*), risk classification, golden dataset.
- **Design:** model choice, guardrails, **fallbacks**, human-in-the-loop points, cost/latency budgets.
- **Build:** prompts, **pinned model versions**.
- **Test:** **eval suites**, rubrics, validated LLM-as-judge, red-teaming, prompt-injection tests, **statistical pass rate**.
- **Deploy:** version model, prompts and data together; canary/shadow rollout; model cards.
- **Maintain:** traces, online evals, drift monitoring. *"Model upgrades = regressions we didn't trigger."*

### 5. Quality criteria for generated code (slide 33)

Compiles and runs, well typed, tested and covered, sound architecture, modular, separation of concerns, extensible, scalable, performance, operating cost, **meets specification**, **verifiable**, **safe**.
**Exercise B passed the first three and failed the last three.**

### 6. Requirements in five lines ⭐

- **Need** (a problem in the world) → **requirement** (an observable property the system must have) → **design decision** (how we chose to do it).
- **FR** = what it does; **quality attribute** = how well (speed, security, accuracy); **constraint** = an imposed limit (language, tool, law).
- A good requirement is **unambiguous, consistent, atomic, prioritised, verifiable**.
- Make quality measurable with **Planguage**: *Scale* (what we measure), *Meter* (how), *Must* (minimum), *Plan* (target).
- **Traceability**: requirement ↔ code ↔ test. **ADR**: *why* a decision was made: context, decision, consequences, alternatives.

### 7. Spec-driven development (slide 53)

- **Spec-first**: write the spec, then the code.
- **Spec-anchored**: the spec is kept and maintained alongside the code.
- **Spec-as-source**: humans edit only the spec, and code is generated from it.
- Tools: OpenSpec, Kiro.

---

## Practice set A: W2 (20 questions)

**1.** Name the four SDLC assumptions that change with AI coding agents.

**2.** With coding agents, where do humans focus, and why?

**3.** "With agents, the spec is *executed*." What does that mean, and what is the risk?

**4.** What is "agent context", and in which SDLC stage does it belong?

**5.** What is *provenance*, and why is it a new Build artifact?

**6.** Why does review become the bottleneck?

**7.** "The agent grades its own work." Explain, and give the fix.

**8.** Why is Deploy called a *trust boundary*?

**9.** How does maintenance change with agents?

**10.** Name three properties that make an LLM *inside the product* different from ordinary components.

**11.** Why does testing an AI-powered product need a *statistical pass rate* instead of pass/fail?

**12.** What does "model upgrades = regressions we didn't trigger" mean? Give a W1 example.

**13.** Classify as need, requirement or design decision:
(a) "Maintainers waste time reading every issue."
(b) "Each triaged issue has a severity from {low, medium, high, critical}."
(c) "Retry once at temperature 0.7."

**14.** Classify as FR, quality attribute or constraint:
(a) "Must be written in Python."
(b) "Critical issues get a 4-hour SLA."
(c) "Issue text must never reach a shell."
(d) "`issue_type` accuracy ≥ 0.85 on dev."

**15.** Rewrite to be verifiable: *"The triage should be accurate and fast."*

**16.** What is wrong with *"The system shall route issues correctly and log errors"*? Use the quality criteria.

**17.** What is an ADR for, and what goes in it?

**18.** Give two uses of traceability and one weakness.

**19.** Spec-first vs spec-anchored vs spec-as-source?

**20.** A PR from an agent says "All tests pass, CI is green". Give three reasons you might still reject it.

---

## Practice set B: W1 + W2 (15 questions)

1. State the course's central premise in one or two sentences.
2. Thread T vs Thread C: define each and give one triage-pipeline example of each.
3. According to Naur, what is the "theory" of a program, and why does it matter when an AI agent writes most of the code?
4. ReactBench: agents passed the behavioural tests yet introduced defects. Why is that possible? What kind of property do tests typically miss?
5. Classify as **need / requirement / design decision**: (a) "Maintainers shouldn't have to read every issue to know if it's theirs." (b) "Use DSPy `Predict` for extraction." (c) "Every triage record includes the model identifier."
6. Classify as **functional / quality attribute / constraint**: (a) "pyright strict reports zero errors." (b) "A `TriageFailure` is routed to `triage-manual`." (c) "`issue_type` macro-F1 ≥ 0.75 on held-out data." (d) "Implemented in Python 3.13."
7. Name the five quality criteria for a requirement. Which criteria does "Important issues must be escalated quickly" violate? Rewrite it so it is verifiable.
8. List the parts of a use case. What goes in an alternate flow for "triage one issue"?
9. What does INVEST stand for? Which letter does *"As a user, I want issues triaged automatically so that things are better"* fail most clearly, and why?
10. Write one Given/When/Then acceptance criterion for the escalation threshold boundary.
11. Jackson: what are *shared phenomena*, and how do requirement R, specification S and domain knowledge W relate?
12. What is a traceability matrix used for? Give two uses and one weakness.
13. What are the sections of an ADR? Why keep ADRs when you already have an SRS?
14. Why does ADR-0002 refuse to coerce `confidence = 1.3` to `1.0`, or `"feature-request"` to `enhancement`?
15. Why is routing kept deterministic and separate from the LLM (ADR-0001)? Name one cost of that choice.

## Answer key: set A

**1.** Coding is expensive; code is the source of truth; behaviour is deterministic, so a test oracle exists; dependencies change only when we upgrade them.

**2.** At the **ends**: specifying (what to build) and verifying (that it's right). Producing code is cheap, while trust is the scarce part.

**3.** A human reading a vague spec asks questions or uses judgment. An agent fills the gaps with **guesses** and builds them. A missing requirement becomes silent, unreviewed behaviour. Example from W1: "run it on 20 issues" became "the first 20, all one repo".

**4.** **Design.** It means conventions and rules files, skills, and tool access/permissions (what the agent may read, run or change). Design now constrains the agent as well as the product.

**5.** A record of who or what wrote the code and who approved it: agent sessions, trajectories, PRs with reviews. When code is generated, you need it to audit and to assign responsibility.

**6.** Agents generate code faster than humans can read it, and reading is the only check that scales to meaning. Exercise B showed this: tools found 1 of 5 defects and reading found 5 of 5.

**7.** If the agent writes both the code and its tests, the tests confirm *what was built*, not *what was required*. They share its blind spots. **Fix:** independent acceptance tests derived from the spec and owned by humans. In Exercise B, 20/20 tests were green while a critical issue got a 72 h SLA.

**8.** It's where changes reach real users. You need **approval gates**, where a human signs off, and an **agent permission policy** that says what an agent may merge or deploy on its own.

**9.** Changes start from the **spec**: update the spec, then regenerate or amend the code. You add **spec–code drift checks**. Maintenance becomes a loop between spec and code, not a stream of patches.

**10.** It is non-deterministic, its interface is natural language, and the supplier keeps changing the model.

**11.** Outputs vary and are sometimes wrong, so there is no single correct oracle. You measure the rate of good outputs on a dataset (e.g. accuracy ≥ 0.85 on dev), with rubrics or a validated LLM-as-judge.

**12.** The provider changes or retires the model, and behaviour shifts without any change to your code. In W1, `gemini-2.5-flash` was retired (404) and the replacement behaved differently (empty answers). Fixes: **pin model versions** and keep **evals** running.

**13.** (a) need · (b) requirement · (c) design decision

**14.** (a) constraint · (b) FR (a business rule the system must apply) · (c) quality attribute (security) · (d) quality attribute (accuracy)

**15.** "`issue_type` accuracy ≥ 0.85 on the dev split's gold-labelled issues, and median latency ≤ 3 s per issue on `gemini-3.5-flash-lite`." Each part has a scale, a meter (how it is measured) and a threshold.

**16.** It is not **atomic**, because it states two requirements. It is not **unambiguous** or **verifiable**, because "correctly" is undefined. Split it in two, and define "correct" by the routing table, e.g. bug → engineering, critical → escalate.

**17.** It records **why** a design decision was made, so the reasoning survives. Sections: Title, Status, Context, Decision, Consequences (good and bad), Alternatives considered.

**18.** Uses: **coverage** (every requirement has code and a test) and **impact analysis** (what breaks if a requirement changes). Weakness: hand-maintained links rot.

**19.** - **Spec-first:** write the spec before the code.
- **Spec-anchored:** keep the spec maintained alongside the code.
- **Spec-as-source:** humans edit only the spec, and the code is regenerated from it.

**20.** Any three of these, all from Exercise B:
- The tests were written by the same agent.
- The stub or fixtures only use clean inputs.
- It breaks the domain vocabulary (`ticket_priority` vs `severity`).
- It duplicates policy (`route_raw` vs `route`).
- It adds an undeclared, possibly typosquatted dependency.
- It has a silent fallback instead of an error.
- It has no logging or spec to verify it against.

## Answer key: set B

1. AI makes writing code cheap; the scarce, valuable work becomes **specifying** what to build and **verifying** that what was built is right.
2. **T** = trust in what the tool/agent did (e.g. reviewing the agent's routing diff whose description says "all tests pass"). **C** = trust in an AI capability inside the shipped product (e.g. whether LLM-assigned severity/confidence is reliable enough to drive escalation).
3. The theory is the programmers' understanding of how the program relates to the world, why it is built as it is, and how to adapt it. It lives in people, not in the text. If an agent writes the code, no human may hold the theory, so modifications decay the design and nobody can judge whether a change is right.
4. Tests check observable behaviour on chosen inputs; a change can satisfy them while degrading **quality attributes** (maintainability, consistency, security, performance) or failing on untested inputs.
5. (a) need · (b) design decision · (c) requirement.
6. (a) quality attribute (QR-03; also arguably a constraint) · (b) functional · (c) quality attribute · (d) constraint.
7. Unambiguous, consistent, atomic, prioritized, verifiable. It violates **unambiguous** ("important", "quickly") and **verifiable**. Rewrite: "The system shall set `escalate = true` iff severity = critical, or severity = high and confidence < 0.6." (Or give an SLA: critical → 4 h.)
8. Name, primary actor, goal, **preconditions**, **main success flow**, **alternate/exception flows**, **postconditions** (plus trigger and stakeholders). Alternate flow: model output fails validation → retry once → still invalid → emit `TriageFailure`, route to `triage-manual`, batch continues.
9. Independent, Negotiable, Valuable, Estimable, Small, Testable. It fails **Testable** (and Valuable/Estimable): "things are better" has no acceptance criterion, and "a user" is no real role.
10. Given a bug with reproduction steps, severity = high, confidence = 0.6, when routing runs, then `escalate = false`. (Add 0.59 → `true` as the pair.)
11. Shared phenomena are events/states visible to **both** the world and the machine (the interface). R is in world terms; S is in shared-phenomena terms; the argument is **S ∧ W ⇒ R**. If the domain assumptions W are false, a machine meeting S still fails R.
12. Uses: **coverage** (every requirement has design/code/test) and **impact analysis** (what changes if a requirement changes). Weakness: hand-maintained matrices **rot** as code changes.
13. Title, Status, Context, Decision, Consequences (+/−), Alternatives considered. An SRS says **what**; an ADR records **why** this option was chosen and what was rejected. That reasoning is lost six months later otherwise.
14. Each coercion is an unstated guess about what the model meant. These guesses accumulate as hidden policy that isn't specified or tested. Rejecting keeps every downstream value trustworthy and makes the failure rate visible and measurable.
15. Policy must be explainable, auditable, testable to 100% of its rules, and changeable without touching a model; model upgrades then can't silently change policy. Cost: the router can only use the five attributes (context outside them is lost), and there are two components to maintain.
