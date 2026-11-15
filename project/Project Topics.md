# Project Topics — Software Engineering with AI 2027

Project topics. Each team of **4 students** picks one at the end of W3 and carries it
through the four milestones (M1 W5, M2 W8, M3 W11, M4 finals). The project is an
instrument for exercising the course's practices: every milestone is graded against what was most recently taught, not against feature count.

| # | Project | AI | Annotated data | Primary metric | Architectural hook |
|---|---|---|---|---|---|
| P1 | **ReceiptLens** — receipts to ledger | VLM | CORD v2 | field F1, total exact match | Arithmetic invariants as runtime contracts driving a bounded repair loop |
| P2 | **AskDB** — natural-language analytics | LLM | BIRD mini-dev | execution accuracy | Generate → statically verify → sandbox-execute → vote on result sets |
| P3 | **ClaimCheck** — multi-hop fact verification | LLM + RAG | HoVer + Wikipedia abstracts | HoVer score | Bounded multi-hop retrieval loop; deterministic citation checker |
| P4 | **LogLens** — log parsing and incident triage | LLM | Loghub-2.0 | grouping / parsing accuracy | LLM only on cache miss: cost engineering architecture |
| P5 | **ClauseScout** — contract review | LLM, long context | CUAD | clause-span precision/recall | Long-context strategies compared (full, map-reduce, retrieval, RLM) |
| P6 | **Concierge** — task-oriented booking assistant | LLM | MultiWOZ 2.4 | joint goal accuracy, task success | Typed dialogue state as the contract; reversible bookings |
| P7 | **ChartReader** — chart de-rendering and QA | VLM | ChartQA | relaxed accuracy, table F1 | Perception/reasoning split; render-and-compare self-check |
| P8 | **Redact** — document de-identification | LLM + rules | TAB (ECHR cases) | identifier recall vs. utility | Privacy-first: the AI component is itself a data-exposure risk |

---

## 1. Requirements common to all projects

### 1.1 AI module
- All projects include an AI module together with deterministic modules (GUI, Business Logic, Backend, DB).
- The AI module consumes an LLM or VLM through an API (OpenRouter, Anthropic, OpenAI,
  Gemini, or a local model via Ollama). Switching provider or model can be achieved as a configuration change; selection must be recorded in an ADR.
- Inputs and outputs are typed and validated at the model boundary (Pydantic / Zod), with
  defined retry, fallback and degradation behaviour. A DSPy (or equivalent) prompt program is expected by M2.
- The M1 scope decision says explicitly where AI is **not** used. Every project below lists deterministic parts that must stay deterministic.
- Each project must define a **baseline**: the simplest credible approach, non-LLM where one exists. The AI module has to beat the baseline on the metric, or the team must argue why it should still ship.
- All dataset content (text, images, logs, cell values) is untrusted input.

### 1.2 Annotated data and evaluation

- Each project is built on a public annotated dataset. This dataset can be snapshot into the repo, or fetched with a checksummed script, together with a fixed `dev` / `test` split. As in the W1 lab, `test` stays sealed until W6 and is scored once.
- Acceptance thresholds (quality, cost per item, latency) are stated in M1 and fixed in M2 **before** the implementation is finished.
- Every project has at least one quality dimension that the dataset does **not** label (listed per project as *Team-labelled dimension*). The team can use an LLM as a Judge and write a rubric. Two team members independently label ≥ 100 items, and the team reports Cohen's κ, then finetune the LLM judge and calibrates it against those labels (W7).
- Every project adds a small **red-team set**: items with injected instructions or adversarial content, scored separately.
- The eval suite runs in CI as a regression gate on a small slice, with statistical acceptance, not single-run pass/fail. The full suite runs on demand.

### 1.3 Architecture

- `docker compose up` brings up the whole system locally. At minimum it has separate deployable units for the domain/application service (API with an OpenAPI contract), the AI component or worker, persistence, and the GUI. The domain core has no import dependency on any LLM SDK.
- OpenTelemetry traces cover every model call, with tokens, cost, latency and model ID as span attributes.
- Monorepo layout as in [Monorepo Workflow](Monorepo%20Workflow.md). The suggested stack is a Python backend and a Next.js / React frontend. Deviations need an ADR.
- Each project has an *architectural hook*: a design question the team must answer with measurements, not opinion.

### 1.4 Three interfaces over one domain model

When designing the project, consider the system will be used through three different interfaces: CLI (command-line interface through a shell command), GUI (graphical user interface on a Web app) and Agentic (an interface - MCP server or CLI used by an AI agent).

All three interfaces call the same application-service layer and contain no business logic. A conformance test checks that the same operation gives the same result through CLI and agent interface.

| Interface | Audience | Required properties |
|---|---|---|
| **CLI** | humans and scripts | porcelain output for humans; `--json` plumbing output with a versioned schema; semantic exit codes; `--dry-run` on every mutation; idempotent where possible |
| **GUI** | humans | web UI centred on **review and correction** of AI output; corrections are stored and feed the improvement log |
| **Agentic** | AI agents | tool server (MCP) exposing small orthogonal primitives; side-effect-free queries; dry-run and reversibility for mutations; structured errors; plus an `AGENTS.md` / skill that teaches an external coding agent to use the system |

M3 requires an **agent task suite** of ≥ 20 realistic tasks per project (examples are listed below). The team measures the success rate of an external agent such as Claude Code on the suite and reports the change attributable to the interface and workflow design.

### 1.5 Team of four

Suggested ownership areas: (a) AI component and evaluation, (b) domain model and persistence, (c) CLI and GUI, (d) agent interface, workflow and CI. Owners lead; they do not work alone.

Every member authors and reviews across areas, and ownership rotates at least once between milestones. Individual contribution is assessed from the repository, the session logs and the reflections.

### 1.6 Milestone deliverables (generic)

| Milestone | Every project delivers |
|---|---|
| **M1 (W5)** | Requirements, each classified and assessed for verifiability; domain model and glossary; system spec; verification placement per major requirement; AI scope decision; dataset snapshot and split; draft thresholds |
| **M2 (W8)** | Typed AI component; baseline; eval harness with thresholds written before implementation completed; `dev` and one-shot `test` numbers; team-labelled dimension with κ and calibrated judge |
| **M3 (W11)** | CLI `--json` and MCP interface with documented stability contract; agent workflow artifacts (instruction file, skills, gates); agent task suite with measured delta |
| **M4 (finals)** | Deployed system; quality-attribute and trustworthiness analysis (Thread T and Thread C); improvement log with failure taxonomy and eval deltas; postmortem; live demo with every claim backed by the eval suite |

---

## 2. Projects

In all the presented projects, the listed information is a starting suggestion to be reviewed and completed in the spec and design stage.  The suggestions indicate the expected scope of the system to be developed.

### P1 — ReceiptLens: receipts to an auditable expense ledger (VLM)

**Pitch.** Photograph receipts; get a clean, auditable ledger. Every posted number either satisfies the receipt's own arithmetic or has been confirmed by a human.

**AI module.** A VLM extracts a structured receipt (merchant, date, line items with quantity / unit price / price, subtotal, tax, service, total) directly from the image. An LLM assigns an expense category. *Not AI:* arithmetic validation, currency normalisation,
duplicate detection (content hash), ledger posting.

**Annotated data.** [CORD v2](https://github.com/clovaai/cord): 1,000 annotated receipts
(800 / 100 / 100), CC BY 4.0, hierarchical field labels including line items.
Metrics: field-level F1, tree-edit-distance accuracy (as used by Donut), total exact match. 
Optional out-of-distribution test on SROIE (English receipts, 4 fields).

*Team-labelled dimension:* expense category and an "auto-post vs. needs review" decision.

*Baseline:* Tesseract OCR + regex for total and date.

**Architecture.** Async pipeline: upload → object store → job queue → VLM extraction worker → validator → auto-post or human review queue. The ledger is event-sourced (corrections are events), so every posting can be reversed and audited.

*Hook:* receipt arithmetic (Σ line items = subtotal; subtotal + tax + service = total) is a runtime contract. When it fails, the worker re-prompts with the violated constraint, within a bounded budget. Measure what the repair loop buys in exact match against what it costs in tokens, and what precision auto-posted receipts actually reach.

**Interfaces.**
- CLI: `receipts ingest ./photos/*.jpg --json`, `receipts review list`, `ledger export --month 2027-01 --format csv`
- GUI: image with extracted fields highlighted side by side, review queue, monthly dashboard
- Agent: `ingest_receipt`, `get_receipt`, `list_review_queue`, `propose_correction` (dry-run), `post_to_ledger`, `query_ledger`
- Agent task example: *"Find March receipts whose line items do not add up to the total and resolve them."*

**Milestone focus.** M1: domain model (Receipt, LineItem, Merchant, LedgerEntry, Correction); define "auto-posted" as a measurable requirement. M4: prompt injection printed *on the receipt image*; throughput and cost for 1,000 receipts.

---

### P2 — AskDB: natural-language analytics over relational data (LLM)

**Pitch.** Analysts ask questions in English and get a correct answer, the SQL that produced it, and a chart. Nothing ever writes to the database.

**AI module.** Schema linking, SQL generation, ambiguity detection (ask a clarifying question instead of guessing), and an NL explanation of the result.

*Not AI:* SQL parsing and validation (e.g. `sqlglot`), read-only enforcement, `LIMIT` injection, execution, charting, caching.

**Annotated data.** [BIRD mini-dev](https://github.com/bird-bench/mini_dev): 500 question / SQL pairs over 11 databases, SQLite / MySQL / PostgreSQL, with "evidence" (external knowledge) per question; CC BY-SA 4.0. Metrics: execution accuracy (EX) and
R-VES (efficiency). Spider dev can be used as a secondary set.

*Team-labelled dimension:* is the question ambiguous or unanswerable from the schema, and is the explanation faithful to the SQL?

*Baseline:* single zero-shot prompt with the full schema.

**Architecture.** Schema-catalog service (introspection, column descriptions, sampled values) → retrieval for schema linking → generator → static verifier (parse, allowlist, `EXPLAIN` cost estimate) → sandboxed read-only executor with timeouts.
*Hook:* execution is the oracle. Generate N candidates, execute them, vote on **result sets** rather than SQL text. Measure accuracy, cost and latency against N.

**Interfaces.**
- CLI: `askdb ask "..." --db california_schools --json`, `askdb validate q.sql`, `askdb eval --split dev`
- GUI: chat, with an editable SQL panel, result table and chart
- Agent: `list_databases`, `describe_table`, `sample_values`, `validate_sql`, `run_query` (limit, timeout), `ask`
- M3 experiment: does an external agent do better with the low-level primitives or with the high-level `ask`?

**Milestone focus.** M1: precise read-only and data-exposure requirements. M4: NL-to-SQL injection ("…and drop the table"), prompt injection hidden in cell values, query-cost budget as a test.

---

### P3 — ClaimCheck: multi-hop fact verification with citations (LLM + RAG)

**Pitch.** Paste a claim; get *supported / not supported* with the exact Wikipedia sentences that justify the verdict, and the retrieval path that found them.

**AI module.** Claim decomposition, iterative query generation (one retrieval per hop), evidence selection, verdict.

*Not AI:* retrieval index (BM25, optionally dense), citation checker (every cited sentence must exist verbatim in a retrieved document), aggregation rule.

**Annotated data.** [HoVer](https://hover-nlp.github.io/): ~26k claims requiring 2–4 hops
over the 2017 Wikipedia abstracts, labelled SUPPORTED / NOT_SUPPORTED with supporting facts (title, sentence id). The corpus and BM25 index are the ones used in the course's
[DSPy demos](../dspy/README.md). Metrics: label accuracy, supporting-fact recall@k, HoVer
score (correct label **and** all supporting facts retrieved).

*Team-labelled dimension:* is the written justification entailed by the cited evidence?

*Baseline:* BM25 top-k + single-shot verdict.

**Architecture.** Retrieval service with an index-build pipeline; verifier as a prompt program (decompose → hop loop → verdict); deterministic citation checker; evidence cache.

*Hook:* a bounded multi-hop loop with an explicit stop condition. Retrieval recall is measured separately from verdict accuracy, so each failure can be attributed to *didn't find* or *found but misjudged*. Optional: compare against an RLM variant.

**Interfaces.**
- CLI: `claimcheck verify "..." --max-hops 4 --json`, `claimcheck search "..."`, `claimcheck cite-check report.md`
- GUI: claim → evidence graph showing each hop, cited sentences highlighted in context
- Agent: `search_corpus`, `get_document`, `verify_claim`, `check_citation`
- Agent task example: *"Write a fact-checked paragraph about X; every sentence must carry a verified citation."*

**Milestone focus.** M1: requirements for abstention ("not enough evidence") versus a verdict. M4: corpus poisoning (planted passages), citation forgery, latency per hop.

---

### P4 — LogLens: log parsing and incident triage at scale (LLM)

**Pitch.** Stream millions of log lines; get stable event templates, anomaly alerts, and a concise incident summary for on-call engineers, at a cost per million lines you can state.

**AI module.** On a cache miss, an LLM turns a raw log line into a template (constants versus variables), using demonstrations selected from previously parsed lines. An LLM also summarises an incident window.

*Not AI:* template-cache matching, template-count time series, anomaly statistics, alert rules.

**Annotated data.** [Loghub-2.0](https://github.com/logpai/loghub-2.0): 14 systems (HDFS, BGL, Thunderbird, Apache, …), ~3.6M lines per system on average, with ground-truth templates. Metrics: grouping accuracy (GA), parsing accuracy (PA), F1 of template accuracy
(FTA). Anomaly labels from the original Loghub (HDFS blocks, BGL alerts) support a secondary detection task. Licence: check the repository before snapshotting.

*Team-labelled dimension:* usefulness and correctness of incident summaries on ~60 incident windows.

*Baseline:* Drain.

**Architecture.** Ingestion (file / tail) → queue → parser service with adaptive template cache → template store → time series → anomaly detector → incident summariser.

*Hook:* cost engineering is the architecture (cf. LILAC, FSE 2024). LLM calls per million lines, cache hit rate and throughput are first-class metrics, stated as tests. The team must also handle cache consistency: what happens when a new line shows that a cached template was wrong?

**Interfaces.**
- CLI: `loglens ingest HDFS.log`, `loglens templates --top 20 --json`, `loglens incidents --since 1h` (pipe-friendly)
- GUI: template explorer, timeline with anomaly spikes, incident view
- Agent: `query_templates`, `get_lines` (template, window), `list_incidents`, `explain_incident`, `annotate_incident`
- Agent task example: *"Investigate the latest incident and report the first anomalous template and the affected components."*

**Milestone focus.** M2: accuracy **and** cost thresholds per system. M4: scalability is the headline quality attribute; attacker-controlled strings inside log lines (user agents, paths) are an injection surface.

---

### P5 — ClauseScout: contract review on long documents (LLM)

**Pitch.** Upload a commercial contract; get the clauses that matter (governing law, cap on liability, auto-renewal, …) highlighted verbatim, checked against your review playbook, and diffed against the previous version. Not legal advice, and the system says so.

**AI module.** Locate and extract clause spans for the CUAD categories, and decide which categories are absent. Compare clauses to a team-written playbook.

*Not AI:* PDF and text segmentation, span grounding (offsets must match verbatim text), version diff, playbook rule evaluation.

**Annotated data.** [CUAD v1](https://www.atticusprojectai.org/cuad): 510 commercial contracts, 41 clause categories, 13,000+ expert labels; CC BY 4.0. Metrics: span-level precision and recall per category, AUPR, precision at 80% recall (as in the CUAD paper),
absence detection accuracy.

*Team-labelled dimension:* risk rating (low / medium / high against the playbook) for ~100 clauses.

*Baseline:* keyword and heading search per category.

**Architecture.** Ingestion → structure-preserving segmentation → extraction strategy →
grounding → playbook check → store, with contract versions and redlines.

*Hook:* contracts run to tens of thousands of tokens. The team compares at least three strategies: full long-context, chunked map-reduce, retrieve-then-extract, and the RLM pattern. For each it measures recall, cost and latency, plus recall as a function of the
clause's **position** in the document (lost in the middle). On a new version, only changed sections are re-processed.

**Interfaces.**
- CLI: `clausescout review msa.pdf --categories cap_on_liability,governing_law --json`, `clausescout diff v1.pdf v2.pdf`
- GUI: document viewer with highlighted clauses, category checklist, risk table
- Agent: `list_contracts`, `find_clause` (contract, category), `get_section`, `compare_versions`, `check_against_playbook`
- Agent task example: *"Which vendor contracts auto-renew within 90 days and lack termination for convenience?"*

**Milestone focus.** M1: missing a clause and flagging a non-clause carry asymmetric costs; state recall thresholds accordingly. M4: trustworthiness (disclaimers, abstention), injection inside contract text.

---

### P6 — Concierge: task-oriented booking assistant (LLM)

**Pitch.** A conversational assistant that books restaurants, hotels, trains and taxis. The conversation is free-form, but the system's state is explicit and typed, and nothing is confirmed without reversible options.

**AI module.** Dialogue state tracking (DST): using turn and session history maintain a typed belief state (domain → slot → value). Generate a new turn given the chosen system action. Design an LLM user simulator to drive end-to-end evaluation.

*Not AI:* dialogue policy (what to ask next), database search, booking transactions, state validation against the ontology.

**Annotated data.** [MultiWOZ 2.4](https://github.com/smartyfh/MultiWOZ2.4): ~10k
[MultiWOZ](https://github.com/budzianowski/multiwoz) for info on the data.
Multi-domain dialogues with corrected validation and test state annotations; ships with the venue databases. Metrics: joint goal accuracy (JGA), slot F1, and end-to-end inform and success rates on simulated dialogues driven by MultiWOZ user goals. 

*Team-labelled dimension:* response faithfulness (no hallucinated venues or attributes) and helpfulness on ~100 turns.

*Baseline:* rule-based slot filling with string matching against the ontology.

**Architecture.** Session service (typed state plus turn log) → DST → deterministic policy → venue DB service → booking service (hold → confirm → cancel) → NLG.

*Hook:* the LLM is confined to perception (DST) and surface realisation (NLG); the typed state is the contract between them. Bookings have legitimate intermediate states (*held*, *awaiting confirmation*), which makes autonomous use by agents safe.

**Interfaces.**
- CLI: `concierge chat` (REPL), and access to non-conversational plumbing `concierge book restaurant --area centre --food italian --people 4 --time 19:00 --json`
- GUI: chat with a live belief-state panel and booking timeline
- Agent: tools supporting `search_venues`, `hold_booking`, `confirm_booking`, `cancel_booking`, `get_session_state`
- M3 experiment: an external agent books for a user, once through the typed primitives and once by *chatting* with Concierge; compare success and cost.

**Milestone focus.** M1: use cases with alternate flows (no availability, user changes their mind). 
M4: governance over irreversible actions, injection through venue descriptions, session isolation.

---

### P7 — ChartReader: chart de-rendering, QA and alt text (VLM)

**Pitch.** Turn a chart image from a report back into its data table. Answer numeric questions about it correctly, and produce alt text a screen-reader user can rely on.

**AI module.** A VLM de-renders the chart into a typed table (series, categories, values, units, axis metadata). An LLM writes a short program over that table to answer a question (program-of-thought). An LLM generates alt text.

*Not AI:* program execution (sandboxed), table validation, re-rendering the extracted table.

**Annotated data.** [ChartQA](https://github.com/vis-nlp/ChartQA) (full version on Hugging
Face): ~20k real-world charts (Statista, Pew, OWID, OECD) with ~32k human-written and
generated questions, plus underlying data tables and annotations; GPL-3.0. Metrics: relaxed
accuracy (5% numeric tolerance) for QA; table-extraction score (relative number-set
similarity / RMS-F1, as in DePlot).

*Team-labelled dimension:* alt-text quality against a rubric (accuracy, salience,
conciseness) on ~100 charts.

*Baseline:* the same VLM answering the question end-to-end from the image.

**Architecture.** Extraction service (VLM) → validated table (equal series lengths, pie shares sum ≈ 100%, axis monotonicity) → reasoning service (code generation + sandbox) → answer; plus an alt-text service.

*Hook:* perception and reasoning are split, and the split must be measured against the end-to-end baseline. Render-and-compare self-check: re-plot the extracted table and have the VLM compare it to the original. Measure what that loop catches and what it costs.

**Interfaces.**
- CLI: `chartreader extract fig.png --csv`, `chartreader ask fig.png "growth 2019–2021?" --json`, `chartreader alt fig.png`
- GUI: original chart, editable extracted table and re-rendered chart side by side; Q&A panel
- Agent: tool support for `extract_table`, `ask_chart`, `render_table`, `compare_render`
- Agent task example: *"Build one comparison table from the five figures in this report and flag inconsistent numbers."*

**Milestone focus.** M1: where numeric precision requirements live on the verification ladder. 
M4: silent numeric error propagation, text-in-image injection, sandbox escape from generated code.

---

### P8 — Redact: document de-identification service (LLM + rules)

**Pitch.** Prepare court decisions and similar documents for publication while presering private information. 
Mask everything that could identify a person, keep the text useful, and record who can reverse a masking.

**AI module.** Context-dependent detection of direct and quasi-identifiers (a profession plus a town plus a year can identify someone). Mask-or-keep decisions, and coreference across mentions so that one person gets one consistent pseudonym.
*Not AI:* regex and checksum detectors for structured PII (emails, phones, ID numbers), pseudonym vault, consistent replacement, policy engine.

**Annotated data.** [Text Anonymization Benchmark (TAB)](https://github.com/NorskRegnesentral/text-anonymization-benchmark):
1,268 English ECHR court cases annotated with entity type, identifier type (direct / quasi / none), confidential attributes and coreference; repository under MIT (confirm before snapshotting). Metrics: TAB's entity-level recall for direct and quasi identifiers
(privacy) and token-level precision (utility).

*Team-labelled dimension:* re-identification risk. An LLM "attacker" tries to re-identify
the person in a masked document; the team labels on ~60 documents whether it succeeded.

*Baseline:* [Presidio (rules + NER)](https://github.com/data-privacy-stack/presidio)

**Architecture.** Detector ensemble (rules, NER, LLM) with a fusion step → coreference-aware pseudonymiser → encrypted vault (pseudonym ↔ original) with access control and an audit log → policy configuration (masking levels).

*Hook:* the AI component is itself a privacy risk, because sending raw documents to an external API exposes the very data being protected. The team must decide and justify, in an ADR backed by measurements, among a local model (Ollama), an external API, or a two-stage design (local pre-masking, then the API on partially masked text). Report the privacy / utility trade-off as a curve, not a single point.

**Interfaces.**
- CLI: `redact run case.txt --policy strict --out masked.txt --json`, `redact reveal <pseudonym>` (privileged, audited)
- GUI: reviewer view with highlighted spans, accept / reject, privacy and utility meters
- Agent: `redact_document`, `list_detections`, `explain_detection`, `set_policy`. There is deliberately **no** `reveal` tool: the capability boundary is part of the design.
- Agent task example: *"Prepare these 20 cases for publication under the strict policy and list every decision that needs human review."*

**Milestone focus.** M1: data-handling constraints as first-class requirements. M4: the security analysis is central (vault, audit, what crosses the trust boundary), and the Thread C analysis must address harm from false negatives.

---

## 3. Selection

By the end of W4 each team submits a ranked list of three projects with a one-paragraph rationale. Before M1, every team must have downloaded its dataset, confirmed its licence and reproduced one published baseline number on a small `dev` slice.
