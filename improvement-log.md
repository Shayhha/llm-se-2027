# Improvement log

Every time the agent gets something wrong, it goes here. Not the fix — the
*failure*, classified.

This file runs for the whole semester. In W12 you will use it to show what
changed about how you work. That only works if it was written as things
happened, so write entries the day they occur. An improvement log
reconstructed from memory in week eleven is a creative writing exercise.

## The taxonomy

Classify every entry as exactly one of:

| Class | Meaning | Where the fix usually belongs |
|---|---|---|
| `capability` | the model could not do this | change the task, or the model |
| `context` | it could have, but did not know something | what the agent is given to read |
| `tool` | it lacked a way to act or to check | tooling |
| `spec` | the request was ambiguous and it guessed | the specification |
| `concept` | it used the wrong idea or the wrong name | the domain model |
| `bug` | ordinary defect, nothing AI-specific | the code |

The class matters more than the fix. Choosing between `context` and `spec`
forces you to say whether the agent lacked information or you did — and those
have different remedies.

---

## Entries

### E1

- **Date**: 2026-11-09
- **What happened**: The first Part 2 run returned `LMRateLimitError` (HTTP 429) for the last 2 of 20 issues (hono#4062, hono#4065). The Gemini free tier refused the burst of calls. `run` reported them as failed rows, mixed with real validation failures.
- **Class**: `tool`. The LM client had no way to wait and retry. The model never answered, so this is not a model failure.
- **Evidence**: notebook Part 2 (cell 13), first run; fix in cell 2 (`num_retries=10`)
- **What I did about it**: added `num_retries=10` to `dspy.LM` (retry with back-off). It is not part of DSPy's cache key, so the 18 cached answers were reused.
- **Did it work?**: yes. Every later run, including the ReAct and optimizer runs (up to 38 calls), had 0 rate-limit failures.

---

### E2

- **Date**: 2026-11-09
- **What happened**: In Part 6 the ReAct agent planned from its memory of the repos instead of the tool's output:
  - for litestar#3782 it looked for a `contrib/` folder (from an older litestar), got an error, relisted the top level three times with growing `max_results`, hit `max_iters=5` without finishing, and answered `app.py`, probably wrong;
  - for hono#4471 its first call used the GitHub path `src/middleware/cors`, which does not exist under the source root.
- **Class**: `context`. It could navigate (it recovered on hono#4471), but it did not know the current layout and that tool paths are relative to the source root.
- **Evidence**: notebook Part 6 (cells 50 and 52, trajectory of litestar#3782)
- **What I did about it**: noted only (the lab asks to observe the trajectory). A fix would put "paths are relative to the source root, e.g. `middleware/cors`" in the tool docstring, or start the agent with the depth-1 list as in Part 4.
- **Did it work?**: not tried.

---

### E3

- **Date**: 2026-11-09
- **What happened**: In Part 7 `BootstrapFewShot` kept the first 3 train issues as demos. Their severity, priority and component are the model's own unverified outputs, because `triage_metric` checks only the type and validity. The demos use GitHub-style paths (`src/client`, `litestar/connection`), and the optimized program went back to `src/...` components that no tool ever returned.
- **Class**: `spec`. The optimizer did what the metric asked; the metric does not say what a good component or severity is.
- **Evidence**: notebook Part 7 (cell 56: the demos printed, then the dev table)
- **What I did about it**: noted only. A metric that also checks that each component is a path `list_components` returns would steer the optimizer.
- **Did it work?**: not tried.
