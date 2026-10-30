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

> DRAFT — written by the agent about its own mistakes in the 2026-10-30
> session. Check each against the session log and rewrite in your own words.

### E1

- **Date**: 2026-10-30
- **What happened**: The agent's retry-once logic could never produce a different answer: the first call ran at temperature 0, and DSPy serves an identical temperature-0 call from its cache, so the "retry" returned the same invalid output. Unit tests with a stub LM passed, so this was invisible until a live run printed `rollout_id has no effect when temperature=0`.
- **Class**: `context` (the agent did not know DSPy's caching behaviour at temperature 0)
- **Evidence**: session log, first 20-issue run (19:07–19:08); fix in `src/triage/extract.py` (`RETRY_TEMPERATURE`)
- **What I did about it**: retry now samples at temperature 0.7 with a new `rollout_id`.
- **Did it work?**: the warning no longer appears; not yet exercised by a real invalid output (the spread run had none).

---

### E2

- **Date**: 2026-10-30
- **What happened**: The agent called `dspy.configure` from `cli.py` and `dspy.context` from the test, outside the one file where `pyproject.toml` relaxes pyright's unknown-type rules. `uv run pyright` failed with 2 errors.
- **Class**: `context` (the rule was written in `pyproject.toml` and in `extract.py`'s docstring; the agent read it and did not apply it)
- **Evidence**: session log, first pyright run; fix moved DSPy calls into `configure_lm` / `triage(lm=...)` in `src/triage/extract.py`
- **What I did about it**: all DSPy calls now live in `extract.py`; tests pass a stub LM as an argument.
- **Did it work?**: yes — `uv run pyright`: 0 errors.

---

### E3

- **Date**: 2026-10-30
- **What happened**: Asked to run on 20 dev issues, the agent took the first 20 — all from hono, because the snapshot is sorted by repo — and sent them in a burst, so 4 of 20 failed with HTTP 429 rate-limit errors that were reported as ordinary triage failures.
- **Class**: `spec` ("run it over twenty issues" did not say which twenty or at what rate; the agent guessed)
- **Evidence**: `runs/dev-20-first-run.jsonl`; fix in `src/triage/cli.py` (`--spread`, `--delay`)
- **What I did about it**: added `--spread` (even sample across the file) and a 4 s default delay between calls.
- **Did it work?**: yes — `runs/dev-20-spread.jsonl` covers all three repos with 0 failures.

---

### E4

- **Date**: 2026-10-30
- **What happened**: The README's model (`gemini/gemini-2.5-flash`) returned 404 ("no longer available to new users"); the replacement Google suggested (`gemini-3.8-flash`) timed out; `gemini-3.5-flash` answered but returned empty text under `verify_env.py`'s 16-token limit because it spends tokens on hidden reasoning.
- **Class**: `capability` (the chosen model could not do the task under the given constraints)
- **Evidence**: session log, `verify_env.py` runs at 16:40–16:50 UTC
- **What I did about it**: switched `LLM_MODEL` to `gemini/gemini-3.5-flash-lite`.
- **Did it work?**: yes — `verify_env.py` all checks passed.
