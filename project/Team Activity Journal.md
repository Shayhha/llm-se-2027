## Team Activity Journal

Each team keeps a journal of its work sessions in the project repository, in `docs/journal.md`. Add one entry per work session (meeting, pair-programming session, review, demo preparation). Newest entries go at the top.

Rules:
- Write the entry at the end of the session, while it is fresh. It should take 5 minutes.
- Be concrete: link the issues, PRs, commits and spec changes you touched.
- "Achieved" reports what actually happened, not what was planned. If something was planned and not done, say so and say why.
- Every "Next" item has an owner and a target date. The next session starts by reviewing these items.

---

### Entry Template

Copy this block for each new session.

```markdown
### YYYY-MM-DD — <short title of the session>

| Field      | Value                                  |
| ---------- | -------------------------------------- |
| Date       | YYYY-MM-DD                             |
| Start      | HH:MM                                  |
| End        | HH:MM                                  |
| Members    | Name1, Name2, Name3 (absent: Name4)    |
| Type       | meeting / pairing / review / demo prep |

#### Planned
- ...
- ...

#### Achieved
- [x] ... (link to PR / issue / commit)
- [ ] ... — not done: <reason>

#### Blockers / Decisions
- Decision: ... (link to ADR if one was written)
- Blocker: ...

#### Next
| Task | Owner | Target date |
| ---- | ----- | ----------- |
| ...  | ...   | YYYY-MM-DD  |
```

---

### Example Entry

### 2026-11-24 — Extraction service: first end-to-end run

| Field      | Value                                |
| ---------- | ------------------------------------ |
| Date       | 2026-11-24                           |
| Start      | 14:00                                |
| End        | 16:30                                |
| Members    | Dana, Yossi, Noa (absent: Amir)      |
| Type       | pairing                              |

#### Planned
- Review the open items from the 2026-11-20 session.
- Implement the `extract_issue_fields` endpoint against the OpenSpec change `add-issue-triage`.
- Add a first evaluation set of 20 labelled issues.

#### Achieved
- [x] Endpoint implemented and merged (PR #14).
- [x] Spec scenario "missing component field" added to `issue-enrichment/spec.md` after we found the case during testing (PR #14).
- [ ] Evaluation set — not done: only 8 issues labelled; the labelling guideline was ambiguous for "priority".

#### Blockers / Decisions
- Decision: validate the LLM output with a Pydantic model at the service boundary (ADR-0002).
- Blocker: need agreement on the definition of "priority" before labelling more issues.

#### Next
| Task                                             | Owner | Target date |
| ------------------------------------------------ | ----- | ----------- |
| Write the labelling guideline for "priority"     | Noa   | 2026-11-26  |
| Label the remaining 12 evaluation issues         | Yossi | 2026-11-28  |
| Add CI job that runs the evaluation on every PR  | Dana  | 2026-11-30  |
