# W3 lab: practice notes

Tasks, tools, concepts, findings and practice questions for the W3 lab. Shorter version:
[TAKEAWAYS.md](TAKEAWAYS.md). All labs:
[../study-notes/labs-practice-guide.md](../study-notes/labs-practice-guide.md).

**Lecture theme:** understanding LLMs: tokens, decoding, attention, training and post-training.
**Lab:** issue triage with DSPy, technique by technique.

## Tasks we had to do

### 0. Preparation (before the lab; submitted on Moodle)
1. Create a **private** repo from the lecturer's template (`llm-se-2027-w3-lab-<user>`).
2. Add the TA (`tpinhas`) as a collaborator.
3. Clone it and fill `.env` (one provider key plus `LLM_MODEL`).
4. Run `uv run python tools/verify_env.py`. All checks must pass; it writes
   `outputs/setup-check-<name>.txt`.
5. Commit and push that file, and submit a txt file with the repo URL on Moodle.

### 1. The lab (`notebooks/w3_lab.ipynb`, all parts on `dev[0:20]`)
1. **Part 1:** connect DSPy to the model.
2. **Part 2:** complete the `TriageIssue` Signature (add `priority` and `component`, and write
   the docstring with the rules), run it, and read the prompt with `dspy.inspect_history`.
3. **Part 3:** write one `dspy.Example` by hand (train[241], litestar#3681) and set `.demos`.
4. **Part 4:** write `forward()` (call the `list_components` tool, then the predictor), then
   extend the tool to `depth=2`.
5. **Part 5:** write the two-step `forward()`: classify, then bug → severity + component,
   enhancement → priority, other → stop.
6. **Part 6:** create a `dspy.ReAct` agent with the tool and `max_iters=5`, and read its
   trajectory.
7. **Part 7:** `BootstrapFewShot(metric, max_bootstrapped_demos=3, max_labeled_demos=0)` and
   `compile` on `trainset(20)`.
8. **Part 8:** print the scoreboard, save `outputs/results/w3_results.json`, and commit
   (notebook, results, `docs/decisions.md`, `improvement-log.md`).
9. Answer the 9 questions in the notebook, and log decisions and agent failures as you go.

## Tools

| Tool | What it was for |
|---|---|
| **DSPy** `dspy.LM`, `dspy.configure` | Connect to the model (via LiteLLM); `num_retries` for rate limits |
| `dspy.Signature`, `InputField`, `OutputField` | Declare a call's inputs, outputs and instruction (the docstring) |
| `dspy.Predict` | Run one signature as one LLM call |
| `dspy.Example`, `.demos` | Few-shot examples in the prompt |
| `dspy.inspect_history` | See the exact prompt and reply DSPy sent |
| `dspy.Module` + `forward()` | A program with several steps or tool calls |
| `dspy.Tool` | How a Python function is shown to the model: name, type hints, docstring |
| `dspy.ReAct` | An agent loop: thought → tool → observation, then a final answer |
| `dspy.BootstrapFewShot` | Optimizer: picks demos by running the program on a train set with a metric |
| Pydantic `TriageRecord` | Validates every prediction (type rules: severity only for bugs …) |
| Jupyter + the `.venv` kernel | Where the lab runs |
| DSPy disk cache | Identical calls are served from cache, so reruns are free |

## Concepts
- **Declarative prompting:** you specify *what* (signature), and the framework writes *how*
  (the prompt).
- **Structured output and contracts:** `Literal` types plus record validation.
- **Zero-shot / one-shot / few-shot,** and where the examples go (earlier conversation turns).
- **Context** (retrieval or tool results given to the model) vs **agentic tool use** (the
  model decides).
- **Workflow / pipeline decomposition** and error propagation.
- **ReAct:** reasoning plus acting; the **trajectory** as evidence; `max_iters` as a cost cap.
- **Prompt optimization:** a metric plus a train set; *bootstrapped* demos are the model's own
  successful traces.
- **Train / dev / test splits:** dev for scores, train for examples, test sealed.
- **Cost, latency and rate limits** as engineering constraints.
- **Tool safety:** read-only, sandboxed paths, untrusted issue text.

## What we found
- Type accuracy and validity were 100% in every part. The 7 labelled issues are easy, and the
  labels are an input. The real differences were in components, cost and calls.
- Free-tier 429 errors at first; fixed with `num_retries=10`.
- Components: guessed `src/...` paths (Parts 2–3) → real top-level folders (depth 1) → real
  specific paths (depth 2) → back to guesses in Part 7 (the optimizer's demos).
- The default tool cap of 50 entries would hide most of the depth-2 list (122–247 entries);
  we used 300.
- ReAct used about 6 calls per issue. One bug failed: it searched a non-existent `contrib/`,
  hit `max_iters`, and answered `app.py`.
- The optimizer stopped after the first 3 train issues: all passed the metric, which checks
  only type and validity.

## Remember
1. A Signature is a contract, and the docstring is the instruction.
2. Examples teach format, not knowledge.
3. Give context when it is small and stable. Let an agent fetch it when it isn't, and pay for
   it in calls.
4. Decomposing a task trades calls for focus and guaranteed shape.
5. An optimizer is only as good as its metric.
6. Read the prompt (`inspect_history`) and the trajectory, not just the score.

## Practice questions (W3)

**1.** What is a DSPy Signature, and where does its docstring end up?
<details><summary>Answer</summary>A class declaring the typed input and output fields of one LLM call. The docstring is the task instruction: DSPy puts it in the system prompt ("your objective is: …") and writes the rest of the prompt and the reply parsing itself.</details>

**2.** Why use `Literal["bug", "enhancement", "other"]` as an output type?
<details><summary>Answer</summary>It is a contract. Only those values are accepted and anything else fails parsing, so downstream code never sees "Bug" or "feature-request" (the W1 "High" vs "high" problem).</details>

**3.** Where does a one-shot example go in the prompt?
<details><summary>Answer</summary>Not in the system prompt. DSPy adds it as a fake earlier turn: a user message with the example input, then an assistant message with the example output in the `[[ ## field ## ]]` format, before the real question.</details>

**4.** Part 4 vs Part 6: what is the difference between giving context and using an agent?
<details><summary>Answer</summary>In Part 4 *our code* calls the tool and always puts the full list in the prompt: one call, a fixed cost, predictable. In Part 6 *the model* decides whether and how to call the tool (path, depth): it is flexible, but it needs many calls (about 6 per issue), and it can go wrong, e.g. by searching a folder that doesn't exist.</details>

**5.** What did the two-step workflow cost, and what did it buy?
<details><summary>Answer</summary>Cost: 38 calls instead of 20 (more latency and rate-limit pressure), but fewer tokens than Part 4, because only bugs carry the component list. Bought: focused prompts per type, records valid by construction, no wasted context for 'other'. Risk: a wrong classification decides every later step.</details>

**6.** What is a ReAct trajectory, and why read it?
<details><summary>Answer</summary>The record of the loop: for each step a thought, the tool name and arguments, and the observation. It is the evidence of *why* the agent answered what it did. Ours showed it planning from stale memory (`contrib/`), wasting steps and hitting `max_iters`.</details>

**7.** How does `BootstrapFewShot` choose demos, and why didn't it help here?
<details><summary>Answer</summary>It runs the program on train examples and keeps traces that pass the metric as demos. Our metric checks only the type and validity, which were already perfect, so it kept the first 3 that passed. Their components and severities are the model's own unverified guesses, and the optimized program's components got worse.</details>

**8.** Why is the `list_components` tool safe to give the model?
<details><summary>Answer</summary>It is read-only, confined to `data/repos/` (`source_dir` rejects absolute paths, `..` and paths outside the snapshot), runs no shell, and `RepoName` is a `Literal`, so only real repos can be chosen. The model's arguments can be steered by issue text, so they must be constrained.</details>

**9.** All parts scored 100%. What does that tell you?
<details><summary>Answer</summary>Very little. Only 7 of 20 issues have a gold type, the labels are part of the input, and severity, priority and component have no gold labels in dev. The score is a sanity check; the real evaluation needs labelled data for the fields that matter (the evaluation topic of later weeks).</details>
