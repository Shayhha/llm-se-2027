# Worksheet: specifications lab

Name: Shay Hahiashvili  Track (cycle 1): **B (stories)**

---

## Cycle 1

### Track A: SRS

**A1.** FR-R-05. Verification method: ……… Test case:

| Input record | Expected `escalate` |
|---|---|
| | |

**A3.** For each requirement you added or changed:

| ID | Fails which 29148 characteristic(s)? | Why |
|---|---|---|
| | | |

Existing requirements CR-1 forced you to change: ……………………

Questions for the triage lead:

1.
2.
3.

### Track B: user stories

**B1.** Rating against each INVEST letter (✓ good · ~ partly · ✗ weak):

| Letter | US-06 Escalate what might be urgent | US-08 Hostile issue text is harmless |
|---|---|---|
| **I**ndependent | ✗ It depends on US-05 (does escalation apply inside `triage-clarify`?) and on enrichment producing a meaningful `confidence` | ~ It cuts across every story that reads issue text (US-01, US-02, US-07), but can be built as a separate safeguard |
| **N**egotiable | ~ The 0.6 threshold and the "critical" rule are fixed in the criteria, but they could be renegotiated | ✓ It states a goal (text is only data) and leaves the mechanism open |
| **V**aluable | ✓ Not missing an outage is clear value for the triage lead | ✓ Preventing command execution or hijacked routing is clear value |
| **E**stimable | ✓ A small, well-understood rule | ~ "Steer routing" has no clear boundary, so the effort is hard to estimate |
| **S**mall | ✓ Size S, three criteria | ~ Size M; it covers three security requirements (SR-01…03) |
| **T**estable | ✓ It has exact boundary tests (0.6 vs below 0.6), but the *value* of the threshold can't be tested until confidence is calibrated | ✗ "Cannot steer routing" can't be proven by a finite set of tests, and "no process started" has no defined check |

- **US-06: weakest letter is I (Independent).** It depends on US-05: does escalation still
  apply inside `triage-clarify`? The story doesn't say, and the README lists this exact
  interaction as an open question. It also depends on enrichment's `confidence` meaning
  something: the 0.6 threshold is only valuable if confidence is calibrated, which no story
  guarantees.
- **US-08: weakest letter is T (Testable).** "Cannot steer routing" can't be proven by a
  finite set of tests. Its criteria check two examples, but there is no oracle for "the
  injected text had no effect" on the values the model chose. "No process is started" doesn't
  say what it is checked against. It is also borderline **S**: it covers three security
  requirements (SR-01…03).

**B2.** Written in `docs/user-stories.md`. CR-1 is too big for one story (it fails S), so it is
split into **US-10** (routing to the private `security` queue, escalate, SLA ≤ 24 h),
**US-11** (the model detects security reports from the text) and **US-12** (an existing
`security` label counts). Existing stories updated because CR-1 made their criteria false:
**US-01** (labels are never used, except now `security`), **US-03** (a failure goes to
`triage-manual`, except a labelled security issue), **US-04** (bug → `engineering`, except
security), **US-05** (no repro → clarify, except security) and **US-06** (security always
escalates).

**B3.** What a coding agent would still have to guess:

1. **How the model signals "security".** A new boolean `is_security_report`, a new
   `issue_type = security`, or a new severity? Each changes the schema, the enum and the eval
   differently. I chose a boolean, but CR-1 doesn't say.
2. **The SLA rule.** "Within 24h max" could mean a flat 24 h, or min(severity SLA, 24 h).
   Does a critical security issue keep 4 h? I chose the min, but that's a guess.
3. **Precedence** when several rules apply: security vs `triage-clarify`, vs `triage-manual`
   for a failed enrichment, and vs any later queue override, such as the component-owner queues.
4. **Where the label comes from.** The input contract (US-01, FR-E-01) only keeps title and
   body, so labels are dropped before routing. The agent must decide how labels reach the
   router, and match them exactly: `security`? `Security`? `security-vulnerability`?
5. **What "flagged to a human straight away" means.** Is it the existing `escalate = true`, or
   a new notification (email/pager)? Is there a time bound for "straight away"?
6. **What "private" means.** Triage can only choose a queue name; who can see the queue is
   decided outside the system. And the issue is *already public* on GitHub: should triage
   also hide or lock it? Out of scope, or not?
7. **The detection threshold and quality target.** How sure must the model be? What recall or
   false-positive rate is acceptable? Without a target, US-11 can't be accepted.
8. **Injection in both directions.** An attacker can write "this is a security issue" to jump
   the queue, or a real report can be worded to look harmless. Is either case acceptable?
9. **Which issue types count.** A *question* about security ("is CSRF protection on by
   default?") is not a vulnerability report. Does it go to `security`?

Existing stories that interact with yours: **US-01** (labels in the input contract),
**US-02** (validating the new field), **US-03** (failure routing), **US-04** (type-based
queue), **US-05** (clarify override), **US-06** (escalation), **US-07** (deterministic rules
and the `reason` field), **US-08** (prompt injection can now flip the security flag),
**US-09** (the evaluation needs security gold labels and a recall target).

### Regroup: compare with your partner from the other track

*(Fill in the right-hand column after talking to your Track A partner. The left column is mine.)*

| My format made explicit… | My partner's format made explicit… |
|---|---|
| **Who** benefits and **why** (role + benefit): the security reviewer, "never left in a public queue" | |
| **Concrete examples** as Given/When/Then: a critical security issue keeps 4 h, a low one gets 24 h | |
| **How big** the change really is: it had to be split into 3 stories, and 5 existing stories changed | |
| **Interactions** with existing behaviour, through criteria that CR-1 made false | |

I would choose an SRS when the system needs **auditability and complete coverage**: numbered
requirements, each with a verification method and a priority, a traceability matrix, and
definitions in one place. Examples are safety or security requirements, contracts, or a spec
an agent must implement without asking questions. I would choose user stories when
**discussing value and scope with stakeholders**, splitting and prioritising work, and
iterating in small steps, where the conversation fills the gaps.

---

## Cycle 2

**C1.** The error was: …………………… The change folder contained, but the main spec no longer
contains: ……………………

**C2.** Requirements in my delta:

| Capability | ADDED / MODIFIED | Requirement name |
|---|---|---|
| | | |

**C3.** A problem `validate` caught: …………………… A problem in my change that it **cannot** catch:
……………………

---

## Cycle 3

### D2: route four issues, assuming all three changes have been archived

| | Record |
|---|---|
| **R1** | `honojs/hono` · `bug` · `component = "router"` · `severity = critical` · no reproduction steps · `confidence = 0.9` · flagged as a security report · 3 👍 |
| **R2** | `Textualize/textual` · `question` · `severity = high` · `confidence = 0.55` · not security · 8 👍 when first triaged, 40 👍 today |
| **R3** | `honojs/hono` · `bug` · `component = "Routing"` (the model's words) · `severity = high` · has reproduction steps · `confidence = 0.8` · not security · 2 👍. `owners.toml` maps (`honojs/hono`, `router`) → `core`. |
| **R4** | `litestar-org/litestar` · **`TriageFailure`** (both model outputs invalid) · a maintainer has added the `security` label · 50 👍 |

| | `queue` | `sla_hours` | `escalate` | Requirement(s) that decide it | **?** and why |
|---|---|---|---|---|---|
| R1 | | | | | |
| R2 | | | | | |
| R3 | | | | | |
| R4 | | | | | |

Other contradictions I found while reading the deltas: ……………………

### D3: domain model

**Glossary.** One sentence per term. In the last column, note where a term is used with
another meaning (which document or change).

| Term | Definition | Used differently in… |
|---|---|---|
| issue | | |
| triage record | | |
| component | | |
| queue | | |
| team / owner | | |
| severity | | |
| priority | | |
| critical | | |
| SLA | | |
| escalate | | |
| security issue | | |

**Invariants.** Rules that must hold *for every* issue, whatever feature is added later.

| # | Invariant ("for every …, …") | Catches problem(s)… |
|---|---|---|
| I1 | | |
| I2 | | |
| I3 | | |
| I4 | | |
| I5 | | |

Where would you put this so that (a) the next `/opsx:propose` reads it and (b) something
**checks** it automatically? ……………………
