# Unspecified decisions

The brief did not tell you everything. Every time you or your agent chose
something the brief did not specify, add a line here.

Examples of the kind of thing that counts: what fields the record has, what
happens to an issue with no clear type, how confident is confident enough,
what the output looks like when the model returns nothing usable.

You will need this list in W2, when we reconstruct the requirements this
build implicitly assumed. The comparison across the cohort is the lesson, so
write down what you actually decided, not what you think is the right answer.

---

- Record fields: `repo`, `number`, `issue_type`, `component`, `severity`, `has_reproduction_steps`, `confidence`, `model` — no queue/SLA (routing is out of scope).
- `issue_type` is one of {bug, enhancement, documentation, question, meta} — the gold-label vocabulary from `config/repos.toml`, not an invented one.
- `severity` is one of {low, medium, high, critical}; there is no gold label for it, so it is unchecked model judgment.
- `component` is free text (lowercase, 1–2 words), not the per-repo component taxonomy; the model's `unknown` becomes `null`.
- `confidence` is the model's self-reported confidence in `issue_type` only, a float in [0, 1]; nothing in the code acts on it.
- The model sees only `repo`, `title` and `body`; labels, comments and author are withheld (labels are where gold comes from).
- The body is truncated to 6,000 characters before it is sent to the model.
- `repo` and `number` are copied from the input, never taken from model output.
- Model output is validated strictly (Pydantic `strict`, `extra="forbid"`); only whitespace/case is normalised, out-of-domain values are rejected, never mapped to the nearest valid one.
- `has_reproduction_steps` must be the literal string `true` or `false`; anything else is invalid.
- On invalid output, retry once (2 attempts total); the retry uses temperature 0.7 so it is not a cache hit of the first answer.
- After two invalid outputs or two failed calls, emit a `TriageFailure` (`reason`, raw output ≤ 2,000 chars) instead of a record; a batch continues past it.
- An issue with no clear type still gets one of the five types — there is no "unknown" type; the low-confidence case is left to confidence.
- First attempt at temperature 0 for repeatability.
- Model: `gemini/gemini-3.5-flash-lite` via DSPy `Predict` (Google retired `gemini-2.5-flash` for new keys; `gemini-3.5-flash` returned empty text under `verify_env`'s 16-token cap).
- CLI input: an issue from `data/snapshot/{train,dev}.json` by `--number`, or any JSON file; `test.json` is refused by the CLI.
- CLI output: one JSON object per line on stdout (record or failure).
- CLI waits 4 s between issues by default because the Gemini free tier rate-limits bursts (HTTP 429).
- `--spread` samples evenly through the file, because the snapshot is sorted by repo and "the first 20" are all hono.
- Issue text is passed only to the model as data; the extraction model has no tools; the signature tells the model to treat instructions inside the issue as content.
