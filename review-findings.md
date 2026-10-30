Name: Shay Hahiashvili
Date: 2026-10-30

# Exercise A - Execution findings

Execute your triage module on at least 20 issues from `data/snapshot/dev.json`. 
Look at the output. Write down anything that surprised you.

> DRAFT — written by the agent from the run outputs in `runs/`. Check each
> one against the files and rewrite in your own words before submitting.

Runs: `runs/dev-20-first-run.jsonl` (first 20 issues of dev.json) and
`runs/dev-20-spread.jsonl` (20 issues evenly spaced across dev.json), model
`gemini/gemini-3.5-flash-lite`.

---
### Surprise 1

- **Input issue json**: `data/snapshot/dev.json`, hono #4121 (gold_type `enhancement`)
- **Output triaged issue**: `{"repo": "hono", "number": 4121, "issue_type": "question", "component": "documentation", "severity": "low", "has_reproduction_steps": false, "confidence": 0.95, ...}`
- **What is surprising**: wrong type, yet confidence 0.95. Across the spread run confidence was 1.0 on 15/20 issues and never below 0.9 — it carries almost no information, so any threshold on it (e.g. "escalate below 0.6") would never fire.

### Surprise 2

- **Input issue json**: the first 20 issues of `dev.json`
- **Output triaged issue**: `runs/dev-20-first-run.jsonl` — all 20 are hono
- **What is surprising**: the snapshot is sorted by repo, so "run it on 20 issues" taken literally tests one repo out of three. Only 5 of those 20 had a gold type at all; the spread sample had 10/20 with gold, 9/10 matched.

### Surprise 3

- **Input issue json**: hono #4041, #4058, #4062, #4065 (first run)
- **Output triaged issue**: `TriageFailure` with `LMRateLimitError` (HTTP 429)
- **What is surprising**: the failures were not bad model output but the Gemini free tier refusing a burst of calls. They came out as the same `TriageFailure` type as a validation failure, so a downstream reader cannot tell "the model was wrong" from "we never asked it". Fixed by pacing calls (`--delay`); the spread run had 0 failures.

### Surprise 4

- **Input issue json**: spread run, all 20
- **Output triaged issue**: severity medium 12 / low 7 / high 1 / critical 0
- **What is surprising**: severity is almost always medium or low, and there is no gold label to check it against — the field the routing step will depend on most is the one we cannot measure.

### Surprise 5

- **Input issue json**: spread run, component field
- **Output triaged issue**: e.g. `netlify adapter`, `sqlalchemy plugin`, `domquery`, `ci`
- **What is surprising**: component is free text with no shared vocabulary, so it cannot be compared with the per-repo gold components in `config/repos.toml` or used as a routing key without another normalisation step.


# Exercise B — Review findings

## Part 1 — found by reading

Record every problem you find in the released diff. One block per finding.
Add as many as you need. Do not delete the unused ones — an empty block is
information too.

**These lock at 1:13.** Once you start running the code, anything new goes in
part 2 instead. That boundary is the measurement: without it there is no way to
tell what reading caught from what the test runner caught.

Confidence: `certain` | `probable` | `uncertain`

---

### Finding 1

- **Location** (file:line):
- **Confidence**:
- **What is wrong**:
- **Why it matters** (what breaks, for whom, when):
- **What would have caught this** (a test? a type? a review rule? nothing?):

---

### Finding 2

- **Location**:
- **Confidence**:
- **What is wrong**:
- **Why it matters**:
- **What would have caught this**:

---

### Finding 3

- **Location**:
- **Confidence**:
- **What is wrong**:
- **Why it matters**:
- **What would have caught this**:

---

### Finding 4

- **Location**:
- **Confidence**:
- **What is wrong**:
- **Why it matters**:
- **What would have caught this**:

---

### Finding 5

- **Location**:
- **Confidence**:
- **What is wrong**:
- **Why it matters**:
- **What would have caught this**:

---

### Finding 6

- **Location**:
- **Confidence**:
- **What is wrong**:
- **Why it matters**:
- **What would have caught this**:

---

## Part 2 — found by running

After `git apply`, `uv run pytest`, `uv run pyright` and the batch run.

### What the tooling found that I did not

- **Which tool** (pytest / pyright / running it):
- **What it showed**:
- **Would I have found this by reading?** (be honest):

### What I found by reading that the tooling did not

- 

### Anything the tooling reported that turned out not to be a problem

- 

---

## Scoring (fill in after the reveal)

| | part 1 (reading) | part 1 + part 2 |
|---|---|---|
| Seeded defects found | | |
| Seeded defects missed | | |
| False positives | | |

**Reading detection rate**: found / (found + missed) = ____%

**Combined detection rate**: found / (found + missed) = ____%

The gap between those two is not a measure of you. It is a measure of which
defects a machine can catch and which ones still need a person — and the
second group is the reason this course exists.

### One sentence: what did you miss, and why do you think you missed it?


