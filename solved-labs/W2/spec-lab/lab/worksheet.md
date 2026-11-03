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

**C1.** The error was: `issue-routing/spec.md: ADDED "Routing Result" must include at least one
scenario`. I fixed it by adding *"Scenario: Result has every field and names its rule"* (an
enhancement routes to `product`, 168 h, no escalation, with a non-empty `reason`). Three
warnings remain (two non-functional sections, one requirement over 500 characters), as
expected.

The change folder contained, but the main spec no longer contains:
- `proposal.md`: the **why** (the motivation), and what is out of scope.
- `design.md`: the technical decisions, the links to the ADRs, and the **open questions**
  (e.g. critical bugs without repro steps).
- `tasks.md`: the 22-task implementation checklist, which archive moved with 0/22 done.
- The **"Non-functional requirements (informative)"** sections of both specs: type safety,
  quality targets (macro-F1 ≥ 0.75), reproducibility, testability, exhaustiveness.

Archive dropped them, as its warnings said. In addition, each main spec's **Purpose** is now
the placeholder "TBD - created by archiving change add-issue-triage". The main specs keep
only *what* the system must do (requirements and scenarios). The *why*, the *how* and the
quality targets survive only in `openspec/changes/archive/2026-11-03-add-issue-triage/`.

**C2.** Requirements in my delta (`openspec/changes/add-security-queue/`):

| Capability | ADDED / MODIFIED | Requirement name |
|---|---|---|
| issue-routing | ADDED | Security Queue (security report → `security`, escalate, takes precedence over every other queue rule, also for a labelled `TriageFailure`) |
| issue-routing | MODIFIED | SLA by Severity (a security report's SLA is capped at 24 h, so critical keeps 4 h) |
| issue-routing | MODIFIED | Clarification Queue for Unreproducible Bugs (except security reports) |
| issue-routing | MODIFIED | Escalation (adds rule 3: every security report escalates) |
| issue-routing | MODIFIED | Enrichment Failures are Routed (only when `security_labelled = false`) |
| issue-enrichment | ADDED | Security Report Detection (new model output `is_security_report`) |
| issue-enrichment | MODIFIED | Enrichment Input Contract (accepts `labels`, never sent to the model, used only for `security_labelled`) |
| issue-enrichment | MODIFIED | Triage Record Schema (adds `is_security_report` from the model and `security_labelled` from the input) |
| issue-enrichment | MODIFIED | Bounded Retry and Explicit Failure (`TriageFailure` carries `security_labelled`) |

**C3.** `openspec validate add-security-queue --strict` → *"Change 'add-security-queue' is
valid"*, with 9 deltas (2 ADDED, 7 MODIFIED).

A problem `validate` caught: when I deleted the scenario from the MODIFIED *"Enrichment
Failures are Routed"*, it reported two errors: *"must include at least one scenario"* and
*"omits scenario(s) the current spec still has: 'Failed enrichment'"*. A MODIFIED block
replaces the whole requirement, so dropping a scenario would silently delete behaviour.

A problem in my change that it **cannot** catch:
- **Meaning and policy.** It can't tell whether "24h max" means a cap or a flat 24 h, whether a
  *question* about security should count, or whether the label override contradicts the
  other teams' in-flight changes. It checks structure, not correctness.
- **Names (observed).** When I renamed a MODIFIED header to *"Escalation Rules"*, a
  requirement that does not exist in the main spec, `validate` reported nothing.
- **Scenario quality.** It only counts scenarios. It doesn't check that they are right, that
  they cover the boundaries, or that the code passes them.

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
D1: after `cp -R lab/in-flight/* openspec/changes/`, `openspec validate --changes --strict`
gives **3 passed, 0 failed**. Every change is valid on its own and all three are valid
together, yet they contradict each other (below). `validate` checks each delta against the
current main spec, never one change against another.

| | `queue` | `sla_hours` | `escalate` | Requirement(s) that decide it | **?** and why |
|---|---|---|---|---|---|
| R1 | **?** `security` or `eng-core` | 4 | true | Queue: *Security Queue* (mine) vs *Queue by Issue Type* (component-owners). SLA: *SLA by Severity*: critical → P1 → 4 (priority version) and critical security → 4 (my version). Escalate: *Escalation* rules 1 and 3 | **Queue ?** My *Security Queue* claims precedence over every queue rule. But component-owners' MODIFIED *Queue by Issue Type* **dropped** the clause "Unless another requirement in this spec overrides it" and now says a bug's queue "SHALL" be `eng-<team>`. Both are SHALL, so they contradict. The archive order decides, and a vulnerability could land in the *public* `eng-core` queue, which is exactly the CR-1 incident. SLA and escalate agree whichever version wins. |
| R2 | `support` | **?** 24 or 4 | true | Queue: *Queue by Issue Type*. SLA: *SLA by Severity* (priority version: high + < 10 👍 → P2 → 24 h; high + ≥ 10 👍 → P1 → 4 h). Escalate: *Escalation* rule 2 (high, 0.55 < 0.6) | **SLA ?** It depends on **when** routing runs: 24 h at first triage (8 👍), 4 h today (40 👍). This breaks *Deterministic Routing* ("no I/O, equal inputs → equal outputs"): 👍 is not in the `TriageRecord`, and priority's task 1.1 fetches it inside `route()`. If my version of *SLA by Severity* is archived last, the answer is 24 regardless. |
| R3 | **?** `engineering` (literally) or `eng-core` (intended) | 24 | false | Queue: *Component Ownership* + *Queue by Issue Type* (owners). SLA: high + 2 👍 → P2 → 24 (also 24 by severity). Escalate: *Escalation* (high, 0.8 ≥ 0.6) | **Queue ?** The model wrote `"Routing"`, but `owners.toml` has `router`. The spec doesn't say whether lookup is exact, case-insensitive, or normalised to a vocabulary. Read literally it's unowned → `engineering`, so the bug misses the team that owns it. `component` is free text in *Triage Record Schema*. |
| R4 | `security` (if the label is present when triage runs), else `triage-manual` **?** | **?** 24, 72 or undefined | **?** true or false | *Security Queue* + *Enrichment Failures are Routed* (mine): a labelled failure → `security`, 24 h, escalate. Without the label: `triage-manual`, 72 h, false. Priority: *Issue Priority* needs a `severity`, and a `TriageFailure` has none | **? (several).** (1) **When** was the label added: before triage, or after? If after, triage never saw it, and nothing re-routes. (2) The priority version of *SLA by Severity* computes the SLA from priority, but a failure has no severity, so it has no priority and no SLA. It also conflicts with the fixed 72 h of *Enrichment Failures are Routed*. (3) 50 👍 would make it P1 if priority applied. |

Other contradictions I found while reading the deltas:
- **Two changes MODIFY the same requirement, *SLA by Severity*** (priority and mine), and a
  MODIFIED block replaces the whole requirement. *Tested in a scratch copy*, archiving in the
  order security → owners → priority: `openspec archive add-priority-score` was **refused**,
  because its block would drop my two security scenarios ("Refresh the change spec before
  archiving"). So archive protects *scenarios*. It does not protect *text*. If the scenarios
  had matched, the last change archived would have won.
- **Component-owners removes the override clause** "Unless another requirement in this spec
  overrides it" from *Queue by Issue Type*. *Security Queue*, *Clarification Queue* and
  *Enrichment Failures are Routed* all depend on it. In the same test, **this archived with no
  error or warning**. The combined spec now contains both "security takes precedence" and "a
  bug's queue SHALL be `eng-<team>`", a contradiction no tool reported.
- **The requirement name lies.** After the priority change, "SLA by **Severity**" computes the
  SLA from priority.
- **"Critical" now means two things.** It means `severity = critical` in *Escalation*, but the
  priority change shows every **P1** as a "critical issue" on the dashboard, and P1 includes
  *high* severity issues with ≥ 10 👍. A "critical issue" on the dashboard may therefore not be
  escalated.
- **Reactions are forbidden input.** *Enrichment Input Contract* says reactions SHALL NOT be
  used, and the priority change makes them decide the deadline.
- **`component = null`** (owners task 2.3) and `"unknown"` are not covered by *Component
  Ownership*, which only defines lookups for named components.
- **No change knows about the others.** Each scenario was written against today's main spec,
  so all of them pass, and none of them test the combination.

### D3: domain model

**Glossary.** One sentence per term. In the last column, note where a term is used with
another meaning (which document or change).

| Term | Definition | Used differently in… |
|---|---|---|
| issue | A GitHub issue at the moment it is triaged: `repo`, `issue_number`, `title`, `body`, and the labels present at that moment. | Priority change: an issue whose 👍 count keeps changing *after* triage. R4: labels added later. |
| triage record | The immutable, validated result of enriching one issue: `TriageRecord` on success, `TriageFailure` on failure. It is the **only** input to routing. | Priority change: routing also reads 👍 from GitHub, outside the record. |
| component | The affected subsystem, a value from a **per-repo controlled vocabulary**, or `null`. | Enrichment: free text from the model (`"Routing"`). Component-owners: a key in `owners.toml` (`router`). |
| queue | The single destination a routing decision sends an issue to. Exactly one per issue. | Security Queue vs component-owners: two rules each assign "the" queue. `security` is also *private*, which is an access property, not a routing one. |
| team / owner | The one team responsible for a component in a repo, from `owners.toml`. | The original spec's "queue" is per *type* (`engineering`). The owners change makes it per *team* (`eng-core`). Two meanings of "who handles it". |
| severity | How bad the technical impact is (low…critical), judged by the model from the text **at triage time**. Never changes afterwards. | Priority change: SLA no longer comes from severity, but the requirement is still named "SLA by Severity". |
| priority | How urgent the response is (P1…P4), derived **deterministically** from fields in the triage record. | Priority change: computed from live 👍, so it is not stable. Exercise B: `ticket_priority` was used as a *synonym* of severity. |
| critical | Only `severity = critical`. | Priority change: "critical issues" on the dashboard = P1, which includes high-severity issues with ≥ 10 👍. |
| SLA | The maximum hours to first response, fixed when the issue is routed. | Priority change: from priority. Mine: from severity, capped at 24 for security. Failure: a flat 72. Three different sources. |
| escalate | Flag the issue to a human on-call **now**, independent of the queue. | CR-1 says "flagged to a human straight away". It could mean `escalate`, or a separate notification. The dashboard's "critical" heading suggests an escalation that doesn't happen. |
| security issue | An issue reporting a vulnerability: the model says `is_security_report = true`, **or** the issue carries the `security` label when triaged. | Enrichment Input Contract: "labels SHALL NOT be used". R4: a label added after triage. |

**Invariants.** Rules that must hold *for every* issue, whatever feature is added later.

| # | Invariant ("for every …, …") | Catches problem(s)… |
|---|---|---|
| I1 | For every routing decision, the result is a pure function of the triage record and versioned static config (no clock, no network, no live GitHub data). Routing the same record twice gives the same result. | R2 (👍 at routing time); priority task 1.1 (fetch in `route()`) |
| I2 | For every issue, exactly **one** queue is chosen, by a **single ordered precedence list** kept in one place: `security` > `triage-manual` > `triage-clarify` > owner/type. A change that adds a queue rule must insert it into that list, not restate "the queue SHALL be…". | R1 (security vs `eng-core`); owners dropping the "unless overridden" clause; R4 (security vs `triage-manual`) |
| I3 | For every security issue, `queue = security`, `escalate = true` and `sla_hours ≤ 24`, whatever other features apply. | R1, R4; the priority change overwriting the security SLA cap |
| I4 | For every `TriageRecord`, `component` is `null` or a member of the repo's component vocabulary, and that vocabulary is the same key set used by `owners.toml`. | R3 (`"Routing"` vs `router`); `null` / `"unknown"` not covered |
| I5 | For every issue (including a `TriageFailure`), `sla_hours` is defined, and no rule may make it **longer** than the SLA its severity alone gives. Features may only shorten deadlines. | R4 (no priority, no SLA); conflicting SLA sources |
| I6 | For every term in the glossary there is one meaning, and every input field a requirement reads is listed in the *Enrichment Input Contract*. | "critical" = P1 on the dashboard; reactions and labels used although the contract forbids them; "SLA by Severity" that isn't by severity |

Where would you put this so that (a) the next `/opsx:propose` reads it and (b) something
**checks** it automatically?
- **(a)** In `openspec/config.yaml` under `context:` (the glossary plus the invariants, which
  OpenSpec injects into every proposal and spec it generates), **and** as a capability
  `openspec/specs/domain-model/spec.md`, with each invariant as a *Requirement* with
  scenarios. A new change then has to MODIFY the invariant explicitly to break it, which
  is visible in review, instead of overwriting another team's requirement by accident.
- **(b)** As **property-based tests** in CI (e.g. Hypothesis over generated `TriageRecord`s,
  `TriageFailure`s and label sets) that assert I1–I5 against the real `route()`. Add a typed
  `Component`/`Queue` vocabulary (`Literal` types, checked by pyright strict) for I4 and I6,
  and a CI step that **archives all open changes into a scratch copy** and runs
  `openspec validate --specs --strict` plus the tests on the combined result. Per-change
  validation can't see the conflicts.
