# Labs practice guide (for quizzes and the final exam)

Each lab's full practice notes live in **that lab's folder**: what we had to do, the tools,
the concepts, what we found, what to remember, and practice questions with answers.

| Lab | Practice notes | Short summary |
|---|---|---|
| W1: issue triage with an LLM + reviewing an agent's change | [`../W1/PRACTICE.md`](../W1/PRACTICE.md) | [`../W1/TAKEAWAYS.md`](../W1/TAKEAWAYS.md) |
| W2: specifications (SRS, user stories, OpenSpec, domain model) | [`../W2/PRACTICE.md`](../W2/PRACTICE.md) | [`../W2/TAKEAWAYS.md`](../W2/TAKEAWAYS.md) |

New labs get a `PRACTICE.md` in their own `solved-labs/WN/` folder and a row here.

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
