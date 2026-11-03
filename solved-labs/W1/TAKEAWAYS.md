# W1 lab: what it taught

**Lecture theme:** AI makes writing code cheap. Specifying what to build, and verifying that it
was built right, are now the hard part.

## Exercise A: build issue triage (one GitHub issue in → one validated `TriageRecord` out)

| Built | The concept behind it |
|---|---|
| Strict Pydantic schema (`extra="forbid"`, enums, `confidence` in [0, 1]) | A **contract** at the border between the stochastic LLM and deterministic code. Invalid output is **rejected, never coerced**. |
| Retry once, then emit a `TriageFailure` | Failure is **explicit and visible**. "We don't know" is data, never a silent default. |
| `repo` and `issue_number` copied from the input | Known facts must not be **re-predicted** by the model. |
| Issue text passed only as a field value | Issue text is **untrusted input** (prompt injection, shell injection). |
| Tests with a stub LM | Tests must be deterministic and free. The real model is neither. |
| `test.json` sealed | A held-out set nobody has looked at keeps evaluation honest. |

**What running it on 20 issues showed** (see [`review-findings.md`](review-findings.md)):
- **Confidence was about 1.0 even when wrong.** Self-reported confidence is not calibrated.
- **"Run it on 20 issues" took the first 20, all from one repo.** The spec was ambiguous and the
  agent guessed. That is a `spec` failure, not a model failure.
- **Rate-limit errors looked like model errors.** Different failure causes need different types.
- **Severity and component have no gold labels.** The fields routing depends on most can't be verified.

## Exercise B: review an agent's change ("All tests pass, CI is green")

- The agent added routing and a batch mode. There were **5 seeded defects**:
  1. two routers that disagree on policy (`route` vs `route_raw`);
  2. case-sensitive severity giving a silent 72 h fallback;
  3. `ticket_priority` as a second name for severity;
  4. a typosquatted, undeclared dependency (`levenshtein_fast`);
  5. no logging, specification or metric.
- **The tools found 1 of 5. Reading found 5 of 5.** pytest passed 20/20 on broken code.
- **Why the tools missed them:**
  - the agent wrote its own tests, so they share its blind spots;
  - the offline stub only emits clean values, which hides the validation bypass;
  - meaning (policy, vocabulary, silent defaults) is invisible to type checkers and tests.

## The improvement log ([`improvement-log.md`](improvement-log.md))

Every agent mistake gets **one** class: `capability`, `context`, `tool`, `spec`, `concept` or
`bug`. Choosing between `context` and `spec` forces you to say whether the *agent* lacked
information or *you* did. They have different fixes.

## Remember for the quiz

1. An LLM is an unreliable component, so put a **strict contract** around it and make failure explicit.
2. **Green CI is evidence only about what was tested.** It isn't evidence about what was required.
3. **When the same agent writes the code and the tests, it grades its own work.**
4. **Stubs and fixtures can hide exactly the inputs that break production.**
5. **One concept, one name** (ubiquitous language).
6. **Supply chain:** every import is a declared, real dependency.
