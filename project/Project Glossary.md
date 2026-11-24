## Project Glossary

Each team keeps a glossary of the domain terms used in its project, in the repository at `docs/glossary.md`. The glossary fixes **one name and one meaning for each concept**. The same names are then used in the PRD, the specs, the code, the tests and the UI.

The glossary matters even more when coding agents work on the project. An agent that is not told what "issue", "ticket" and "case" mean will treat them as three concepts, or merge two concepts that should stay distinct. Reference the glossary from `AGENTS.md` / `CLAUDE.md` so the agent reads it before writing specs or code.

Rules:
- One entry per concept. If two words name the same concept, pick one as the **preferred term** and list the other under **Avoid**.
- The definition says what the thing *is* in this project, not in general. Include what it is *not* when there is a likely confusion.
- Give the **code name** (class, table, field, endpoint) so readers can map the term to the implementation.
- Keep entries in alphabetical order.
- Update the glossary in the same PR that introduces or changes a term in a spec or in the code.
- When a term is ambiguous or disputed, record the decision and link the ADR or issue where it was settled.

---

### Entry Template

Copy this block for each new term.

```markdown
### <Preferred Term>

**Definition:** One or two sentences: what this concept means in the project.

**Not to be confused with:** <other term> — <the difference>.

**Avoid:** <synonyms not to use>

**Code name:** `ClassName` / `table_name` / `field_name` / `GET /endpoint`

**Example:** A concrete instance.

**Related:** [[Term A]], [[Term B]]

**Source / decision:** PRD §x, `openspec/specs/<capability>/spec.md`, ADR-000N
```

For a compact glossary with many short terms, a table can be used instead:

```markdown
| Term | Definition | Avoid | Code name | Related |
| ---- | ---------- | ----- | --------- | ------- |
|      |            |       |           |         |
```

---

### Example Entries

#### Component

**Definition:** A part of the product that an issue can be assigned to (for example `auth`, `billing`, `ui`). Each component has exactly one owning team.

**Not to be confused with:** *Label* — a free-form tag on the GitHub issue. A component is one value from a closed list; an issue can have many labels.

**Avoid:** module, area, subsystem

**Code name:** `Component` (enum), `issue.component`

**Example:** An issue "Login button does nothing on Safari" has component `auth`.

**Related:** [[Owner]], [[Routing]]

**Source / decision:** `openspec/specs/issue-routing/spec.md`

#### Confidence

**Definition:** A score in [0, 1] that the extraction step attaches to each extracted field. It measures how sure the model is of the value. It is not a probability that the issue is routed correctly.

**Avoid:** certainty, score (alone)

**Code name:** `ExtractedField.confidence`

**Example:** `component = "auth"`, `confidence = 0.42`. Below the threshold, so the issue is escalated.

**Related:** [[Escalation]], [[Extraction]]

**Source / decision:** ADR-0005 (escalate on low confidence)

#### Escalation

**Definition:** Sending an issue to a human triager instead of routing it automatically. This happens when any required field has confidence below the threshold, or when validation fails.

**Not to be confused with:** *Priority* — escalation is about who handles the triage, not how urgent the issue is.

**Avoid:** fallback, manual mode

**Code name:** `RoutingDecision.ESCALATE`

**Related:** [[Confidence]], [[Routing]]

**Source / decision:** ADR-0005

#### Issue

**Definition:** A bug report or feature request submitted on GitHub. Its text is the input to the triage pipeline and is treated as untrusted.

**Avoid:** ticket, case, request

**Code name:** `Issue`, `issues` table

**Related:** [[Extraction]], [[Routing]]

**Source / decision:** ADR-0004 (issue text is untrusted)
