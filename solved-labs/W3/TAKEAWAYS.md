# W3 lab: what it taught

**Lab theme:** build the W1 issue triage yourself with **DSPy**, one technique at a time, on
the same 20 dev issues, and watch what each technique changes and costs.
Graded copy: private repo `Shayhha/llm-se-2027-w3-lab-Shayhha`. Notebook:
[`notebooks/w3_lab.ipynb`](notebooks/w3_lab.ipynb).

## What each part showed

| Part | Technique | Score (type / valid) | Calls · cost | What it showed |
|---|---|---|---|---|
| 1 | Connect (`dspy.LM`, `dspy.configure`) | — | — | Free-tier rate limits (429) need retries (`num_retries`) |
| 2 | Zero-shot **Signature** with `Literal` outputs | 100% / 100% | 20 · $0.0084 | The output type is a contract. Components are guessed from memory (`src/...`). |
| 3 | **One-shot** (`.demos = [example]`) | 100% / 100% | 20 · $0.0102 | The example becomes a fake earlier user/assistant turn. One example from another repo barely changes the vocabulary. |
| 4 | **Tool + context** in a **Module** (`forward()`) | 100% / 100% | 20 · $0.0127 | With the repo's real folder list, components become real and specific (`middleware/cors/`), at +50% tokens |
| 5 | **Two-step workflow** (classify, then type-specific step) | 100% / 100% | 38 · $0.0102 | More calls, each simpler. Type-valid by construction. A first-step mistake decides everything after it. |
| 6 | **ReAct agent** (the model calls the tool itself) | not scored | 31 calls / 5 bugs | Thought → tool call → observation. It planned from stale memory (`contrib/`), hit `max_iters`, and answered wrong. |
| 7 | **Optimizer** (`BootstrapFewShot`) | 100% / 100% | 20 · $0.0149 | It kept the first 3 train issues that passed the metric. The demos' components are the model's own unchecked guesses. |

## Remember for the quiz

1. **Signature** = declared inputs and outputs, with the docstring as the instruction; DSPy
   writes the prompt and parses the reply. **Module** = a program of steps in `forward()`.
2. **Structured output:** `Literal` types make the model's reply fit a contract. Validation
   still matters (W1's "High" vs "high").
3. **Zero → one → few-shot:** examples enter the prompt as earlier conversation turns. They
   teach format and style more than knowledge.
4. **Context injection vs agents:** you either *give* the model the context (Part 4: fixed
   cost, predictable) or let it *fetch* the context (ReAct: flexible, but more calls, and it
   can wander or fail).
5. **Workflows:** splitting a task gives focused prompts and guaranteed-valid shapes, but the
   first step's error propagates.
6. **An optimizer optimizes the metric, not your intent.** A metric that checks only the type
   cannot improve severity or component.
7. **Every technique trades accuracy against cost.** Watch calls, tokens and latency, and the
   free-tier rate limits.
8. **Tools are an attack surface.** The tool is read-only and confined to `data/repos/`
   (`source_dir` rejects `..` and absolute paths). Issue text stays data.
9. **Scores can hide everything.** 100% on 7 easy labelled issues said nothing about severity
   or component, which have no gold labels in dev.
