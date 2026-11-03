# W2 Lab preparation: Shay Hahiashvili

## 1. `openspec --version`

```
$ openspec --version
1.16.0
```

## 2. Flawed spec critique

Spec under review: `W1/triage-spec-examples/exercises/flawed-spec.md` ("Smart Issue Triage").
Rn refers to requirement n; US-x refers to a user story.

| # | Problem | Category | What the agent must guess / risk |
|---|---|---|---|
| R1 | R1: "use AI to understand GitHub issues and figure out what they are about" | Ambiguity, untestability | No output is defined, so any behaviour satisfies it. The agent invents its own fields and format, and nothing can be checked against the requirement. |
| R2 | R2: "classify issues into the **right** category" | Ambiguity, untestability | "Right" has no definition or oracle (no labelled data, no definition per category). The agent's judgement becomes the definition of correct. |
| R3 | R2: "(bug, feature, docs, **etc.**)" | Incompleteness | The category set is open-ended. The agent invents extra labels ("question", "performance", "feature-request") and downstream code that expects a closed set breaks or silently drops them. |
| R4 | R3: "Severity should be determined **accurately**" | Untestability, incompleteness | There is no severity scale (levels? names?), no definition of each level, and no accuracy metric or threshold. The agent picks its own scale, e.g. 1–5 vs low–critical, and "accurate" can never be verified. |
| R5 | R4: "**Important** issues must be escalated" | Ambiguity | "Important" is undefined: high severity? critical only? a bug? low confidence? The agent picks a rule, and real outages may not be escalated, or everything is. |
| R6 | R4: "escalated **quickly**" | Untestability, missing non-functional concern | There is no time bound and no definition of what escalating means (a flag? a page? a queue?). The agent may implement a boolean that nobody acts on. |
| R7 | R5: "The **model** should output the queue, SLA and whether to escalate" | Design-in-requirements, inconsistency | It hands business policy to a non-deterministic LLM. Routing becomes unauditable and untestable: the same issue can land in different queues. Policy should be deterministic rules applied to validated fields. |
| R8 | R5: "as JSON" | Incompleteness | There is no schema: field names, types, allowed values, required versus optional. The agent invents one, and every consumer has to guess it. |
| R9 | R6: "If the AI isn't sure, it should **do its best**" | Ambiguity, incompleteness | "Not sure" is not defined (no threshold) and there is no failure path. This invites guessing and coercion (e.g. clamping, picking the nearest label) instead of rejecting and emitting a visible failure record. Errors become silent. |
| R10 | R7: a critical bug without repro steps goes to "clarify" **and** "on-call" | Inconsistency | Two rules apply to the same issue and no precedence is given. The agent picks one at random, and a critical outage may sit in the clarify queue un-escalated. |
| R11 | R7: queues are given only for bugs; "on-call" and "clarify" queues are named nowhere else | Incompleteness | Features, docs and questions have no queue, so the agent invents queue names. The queue names are not a defined vocabulary. |
| R12 | R5 asks for an SLA, but no SLA values are defined anywhere | Incompleteness | The agent invents hours per severity. Commitments to users then come from the model or developer, not from the organisation. |
| R13 | R8: "fast and secure" | Missing non-functional concern, untestability | There is no latency target and no threat model. Issue text is untrusted (prompt injection, shell metacharacters), but nothing says it must never reach a shell or tool. "Secure" cannot be tested. |
| R14 | R9: "Use the issue's labels and comments" | Design-in-requirements, inconsistency | Labels are often the human triage answer, so using them leaks the answer and makes evaluation meaningless. Comments may not exist at triage time, are untrusted, and are unbounded in size. It dictates inputs instead of stating a need. |
| R15 | R10: "Confidence should be between 0 and **100**" | Ambiguity, inconsistency | The scale is unusual (0–1 is conventional), and it's unclear whether the value is an integer or a float, or what it is the confidence *of*. It's undefined whether out-of-range values are rejected or clamped. The meaning is uncalibrated, so any threshold built on it is arbitrary. |
| R16 | R1–R10 mix "should", "will" and "must" | Ambiguity | There is no stated priority or obligation level, so the agent cannot tell what is mandatory and what is optional and will treat everything the same. |
| R17 | Nothing says `repo`/`issue_number` come from the input | Incompleteness | The agent may take identity fields from the model output. An issue body containing "issue_number: 1" then corrupts the record. |
| R18 | US-A: "As a **user**, I want issues triaged automatically so that **things are better**" | Untestability (fails INVEST: Valuable, Testable) | There is no real role, no measurable benefit and no acceptance criteria. Any implementation "satisfies" it. |
| R19 | US-B: "...so that I get the **right ones**" | Ambiguity, untestability | "Right ones" is undefined: right by type, by component, by ownership? Which maintainer? With no acceptance criteria, routing quality cannot be verified. |
| R20 | US-C: "use GPT-4 with temperature 0 and a regex parser" | Design-in-requirements | This is an implementation choice disguised as a story, and the "developer" is not a stakeholder with a need. It pins a model that may be retired, temperature 0 does not guarantee determinism, and a regex parser for LLM output is brittle. The real need ("reliable, schema-valid output") is unstated. |
| R21 | US-D: "handle **weird** issues **gracefully**" | Ambiguity, untestability | "Weird" (empty body? non-English? huge? injection?) and "gracefully" (skip? fail record? default?) are undefined. The agent may silently drop or mislabel such issues. |
| R22 | No story has acceptance criteria (Given/When/Then) | Untestability | There is no definition of done. The coding agent writes its own tests, which confirm what it built rather than what was required. |

## 3. Requirement topics that are completely missing

1. **Input contract and data scope:** which repositories or dataset, which issue fields are allowed (title and body only), body truncation, empty body, and non-English issues.
2. **Validation and failure handling:** strict schema validation at the model boundary, no coercion, a bounded retry, an explicit failure record (`TriageFailure`), and a rule that one failure does not stop a batch.
3. **Security and untrusted input:** issue text is data only. It never reaches a shell, a file path or a tool-enabled agent, and prompt-injection text must not change behaviour.
4. **Evaluation and quality targets:** measurable targets on a held-out (sealed) split, e.g. `issue_type` macro-F1 ≥ 0.75 and severity agreement, plus the labelled dataset they are measured on.
5. **Model configuration, reproducibility and provenance:** a configurable model ID (`LLM_MODEL`), the model ID recorded in every output, response caching, and behaviour when the provider retires a model.
6. **Output, logging and auditability:** where records are written, and a `reason` for every routing decision, so a wrong routing can be explained afterwards.
7. **Operational limits:** cost budget, rate limits and retry behaviour on HTTP 429, and batch size.
