# Quiz W3 cheat sheet: the 13 things to remember

Week-3 quiz: Foundation Models (deck 02, slides 1–27) + the W2 specifications lab.
Full notes: `quiz-w3-prep.md`.

## Lecture: Foundation Models

**1. Classical software vs ML.** Classical software is a hand-written algorithm, so it is
**deterministic**. ML learns a **model from data**, so it is **probabilistic**.

**2. The four ML traits:**
- **probabilistic:** the same input can give different answers;
- **uncertain:** it can answer with low confidence, or not know;
- **biased** by its training data (when real data differs from training data, the bias is
  unpredictable);
- **the most likely answer is not always the best action.**

**3. A language model predicts the next token** from the context, as a probability
distribution; generating text means repeating this. **Plain text is enough to train it, with
no labels**, which is why huge models became possible.

**4. Pre-training vs post-training.**

| | Pre-training | Post-training |
|---|---|---|
| Data | trillions of tokens | thousands of examples |
| Cost | $10–100M | $10–100K |
| Result | a **"lossy zip of the internet"**: knowledge in the weights, up to a **training cutoff date** | a helpful chat assistant (**instruction fine-tuning + preference alignment**) |

The three stages: **pre-training → fine-tuning → alignment**.

**5. Multi-task text-to-text training** lets a model do **new tasks from a description alone**
(zero-shot generalization).

**6. A foundation model is one component** of a larger AI system, not the whole system.

**7. Prompting:**
- **zero-shot:** no examples;
- **few-shot:** examples in the prompt;
- **chain of thought:** ask it to think step by step;
- **temperature:** creative vs precise;
- **more context** helps, up to a limit and at a cost.

**8. Prompting is fragile and costly.**
- A **small prompt change can cause a big change in the result**.
- Choosing examples is real work.
- Parse the answer more reliably by asking for **JSON**.
- You need a **benchmark**: test data, a metric, and repeatable runs.

## W2 lab: specifications

**9. INVEST** = Independent, Negotiable, Valuable, Estimable, Small, Testable. CR-1 failed
**Small**, so it was split into 3 stories.

**10. A valid spec isn't a correct spec.** `openspec validate` checks **form, not meaning**.
Changes that each pass validation can still **contradict each other** when combined.

**11. A MODIFIED requirement replaces the whole block.** **Archive drops the "why"** and keeps
only requirements and scenarios.

**12. One term, one meaning.** A **domain model** (a glossary plus "for every issue, …" rules)
prevents conflicts.

**13. With AI agents, the spec is executed.** Every gap becomes the agent's guess.

## The one link to make

The model is **probabilistic** and **remembers only up to its cutoff**. So we keep decisions
(routing) **deterministic**, **validate** everything the model outputs, and give it **current
context** through tools instead of trusting its memory.

---

# Quick self-test

Cover the sheet and answer from memory. The answers are on the next page.

1. Classical software vs ML: one word for how each behaves.
2. Name the four ML traits.
3. What does a language model predict, and why was no labelling needed?
4. Pre-training vs post-training: scale, cost, result.
5. What is the "lossy zip of the internet", and what is its limit?
6. Name the three stages of building a foundation model.
7. What does multi-task text-to-text training make possible?
8. Zero-shot vs few-shot vs chain of thought.
9. What does temperature control?
10. Give two reasons prompting is fragile or costly.
11. What does INVEST stand for, and which letter did CR-1 fail?
12. Can three changes that each pass `validate --strict` be wrong together? Why?
13. What does a MODIFIED requirement do, and what does archive drop?
14. What is a domain model?
15. Why do we keep routing deterministic when the model is an LLM?

# Self-test answers

1. Classical: **deterministic**. ML: **probabilistic**.
2. Probabilistic; uncertain; biased by training data; the most likely answer isn't always the
   best action.
3. The **next token**, given the context. The next word in plain text *is* the label, so the
   training is self-supervised.
4. Pre-training: trillions of tokens, $10–100M, broad knowledge. Post-training: thousands of
   examples, $10–100K, a helpful aligned assistant.
5. The knowledge stored in the model's weights (parametric memory). Its limit is the
   **training cutoff date**: nothing newer is known, and the rest is lossy.
6. Pre-training → fine-tuning → alignment.
7. Doing **new tasks from a description alone** (zero-shot generalization).
8. Zero-shot: no examples. Few-shot: examples in the prompt. Chain of thought: reason step by
   step first.
9. Randomness: higher is more creative and diverse, lower is more precise and repeatable.
10. Any two: a small prompt change gives a big result change; choosing examples; parsing the
    answer (use JSON); needing a benchmark (test data + metric + repeatable runs).
11. Independent, Negotiable, Valuable, Estimable, Small, Testable. It failed **Small**.
12. Yes. Each is validated against today's spec, not against the others, and validation
    checks form, not meaning.
13. It **replaces the whole requirement block** (copy it in full). Archive drops the proposal
    (the "why"), the design and open questions, and the quality targets.
14. A glossary (one meaning per term) plus invariants ("for every issue, …") that every change
    must respect.
15. The model is probabilistic. Decisions must be repeatable, explainable and testable, so the
    model only extracts fields, and validated rules decide.
