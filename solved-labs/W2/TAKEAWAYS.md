# W2 lab: what it taught

**Lecture theme:** the software lifecycle and requirements. What changes when an AI agent
writes the code, and how to write requirements an agent can't misread.

## Lab preparation ([`lab-prep/w2-lab-prep.md`](lab-prep/w2-lab-prep.md))

- Installed OpenSpec (`openspec --version` → 1.16.0).
- Critiqued a deliberately weak spec. It had 22 problems, each classified as ambiguity,
  incompleteness, inconsistency, untestability, design-in-requirements or a missing
  non-functional concern. The question for each was: *what would a coding agent have to
  guess, and what goes wrong if it guesses differently?*

## In-class specifications lab ([`spec-lab/lab/worksheet.md`](spec-lab/lab/worksheet.md))

Every cycle used one change request, **CR-1**: *"security reports go to a private queue, are
flagged to a human straight away, and are handled within 24 h."*

| Cycle | What I did | What it showed |
|---|---|---|
| 1. User stories (track B) | Rated US-06/US-08 against INVEST. Split CR-1 into US-10–12 and updated the 5 stories it made false ([`docs/user-stories.md`](spec-lab/docs/user-stories.md)). Listed 9 guesses an agent would still have to make. | A "small change" touched routing, the model and the input contract. Stories show value and interactions but leave many decisions open. |
| 2. OpenSpec | Fixed and archived `add-issue-triage`. Wrote the change `add-security-queue` (2 ADDED + 7 MODIFIED requirements). It validated. | Archive keeps only requirements and scenarios; the *why*, the design and the quality targets are dropped. **`validate` checks structure, not meaning.** |
| 3. Composing changes | Added two other teams' changes, routed issues R1–R4 with all three applied, then wrote a glossary and invariants. | Three individually valid changes produce a system that can't route R1–R4 consistently. |

**Cycle 3 conflicts to know:**
- The owners change silently dropped the "unless overridden" clause, so a security bug
  could go to the public `eng-core` queue.
- Priority uses live 👍 counts, so the same issue gets different SLAs at different times. That
  breaks deterministic routing.
- `"Routing"` (the model's words) ≠ `router` (`owners.toml`): a free-text component defeats lookup.
- "Critical" means `severity = critical` in one place and P1 on the dashboard in another.
- A failed triage that carries a security label has no defined SLA.

## Remember for the quiz

1. **A spec that passes validation isn't correct.** Tools check format. People check meaning.
2. **Changes that are each valid can combine into an invalid system.** No one tests the combination.
3. **A MODIFIED requirement replaces the whole block.** Copy the original in full.
4. **One term, one meaning.** A **domain model** (glossary plus "for every …" invariants) prevents drift.
5. **Routing must be deterministic.** Never depend on live or time-varying data.
6. **Format trade-offs:**
   - user stories show value, size and interactions;
   - an SRS or OpenSpec gives precise, checkable requirements with traceability;
   - none of them sees conflicts *between* changes.
7. **With agents, the spec is executed.** Every gap becomes the agent's guess.
