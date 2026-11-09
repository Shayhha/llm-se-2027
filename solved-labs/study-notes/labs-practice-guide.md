# Labs practice guide (for quizzes and the final exam)

Each lab's full practice notes live in **that lab's folder**: what we had to do, the tools,
the concepts, what we found, what to remember, and practice questions with answers.

| Lab | Practice notes | Short summary |
|---|---|---|---|
| W1: issue triage with an LLM + reviewing an agent's change | [`../W1/PRACTICE.md`](../W1/PRACTICE.md) | [`../W1/TAKEAWAYS.md`](../W1/TAKEAWAYS.md) |
| W2: specifications (SRS, user stories, OpenSpec, domain model) | [`../W2/PRACTICE.md`](../W2/PRACTICE.md) | [`../W2/TAKEAWAYS.md`](../W2/TAKEAWAYS.md) |
| W3: issue triage with DSPy (signatures, examples, tools, workflows, ReAct, optimizers) | [`../W3/PRACTICE.md`](../W3/PRACTICE.md) | [`../W3/TAKEAWAYS.md`](../W3/TAKEAWAYS.md) |

New labs get a `PRACTICE.md` in their own `solved-labs/WN/` folder and a row here.

---

# Across the labs

| Theme | W1 | W2 | W3 |
|---|---|---|
| Tools check form, not meaning | pytest 20/20 green, 4 of 5 defects missed | `validate` passes 3 conflicting changes | 100% on every part while components got worse in Part 7 |
| Vocabulary drift | `ticket_priority` vs `severity` | "critical", "priority", "component" with two meanings | severity vs priority kept separate by the schema |
| Silent policy loss | `route_raw` drops two routing rules | a MODIFIED block drops the "unless overridden" clause | the optimizer's metric ignores component, so it degrades |
| Determinism | the stub LM, temperature 0 and the cache | routing must not read live 👍 or late labels | DSPy cache; `temperature` and retries |
| Gaps get guessed | "first 20 issues" | 9 guesses in the agent test | the agent guessed a `contrib/` folder from memory |
| Human role | review the diff against the spec | write the spec, glossary and invariants | choose the context, the metric, and read the trajectory |
