# Quiz prep: week 3 quiz

**Scope:** the previous week's lecture (deck 2027-02, **slides 1–27: "Foundation Models –
Basics"**) and the previous week's lab (**W2: specifications**). Format: 5–10 minutes, short
conceptual questions. Practice questions with answers are at the end.

---

# Part A: lecture, Foundation Models basics (slides 1–27)

## 0. The lecture's objectives (slides 1–3)
Part 4 of the course, **"Foundation Models – Basics"**: FMs are the engines of modern AI
applications, pre-trained assistants that can adapt to many tasks. The lecture asks:
1. What are foundation models?
2. How are they built?
3. Why do they matter?
4. What are their costs, opportunities and risks?
5. How are they expected to evolve?

## 1. What AI is, and why now (slides 2–4)
- **AI:** a machine performing cognitive functions we associate with human minds: perceiving,
  reasoning, learning, interacting with the environment, problem solving, creativity.
- **Why now:** three factors converged:
  1. better **algorithms and machine-learning understanding**;
  2. **data** availability;
  3. growth in **computing power and storage**.

## 2. Classical software vs machine learning (slides 5–11)

**Running example: real-estate appraisal.**

| | Classical software engineering | Machine learning |
|---|---|---|
| Parts of the system | **algorithm**, **data model**, **input/output**, **user interface** (slide 6) | **features**, a **dataset**, a generic learning algorithm, a trained **model** (slides 8–9) |
| How it's built | a domain expert and a product manager design a **deterministic algorithm**; you write the data model and logic | a **generic learning algorithm** learns a **model** from a **dataset** of examples (features → price) |
| Input → output | data model → algorithm → output | **features** → model → prediction |
| Behaviour | deterministic: same input → same output | **probabilistic** |
| Where the knowledge lives | in the code | in the **data**, and in the model trained on it |

- **Training** = *memorize* the examples and *generalize* to new ones.
- **ML tasks:** predict (a property's price), classify (spam), recommend (movies).
- **The work of data science** (slide 10):
  - how to extract and select features;
  - how to encode them;
  - how to learn a model;
  - how to **evaluate** it for future predictions.
- **ML costs:** data collection and curation; model serving and maintenance; keeping metrics
  valid as **data drifts**.

**ML characteristics (slide 11), know these well:**
1. **Probabilistic:** it can give **different answers to the same input**.
2. **Uncertainty:** answers can come with a wide uncertainty window, and the model can decide
   it doesn't know.
3. **Biases:** it depends on the data distribution seen at training time. When training data
   and inference-time data differ, it produces **unpredictable biases**.
4. **Acting on predictions:** the most likely answer is not always the best action, especially
   for repeated actions.

**The data era (2000–2020):** data became valuable, **annotation was expensive**, and the big
ML wins were ad placement, recommendation, attention-grabbing feeds and machine translation.

## 3. Foundation models: where they came from (slides 13–20)

**Key moments (slide 14):**

| Year | Milestone | Why it matters |
|---|---|---|
| 2012 | ImageNet with CNNs | neural networks work at scale |
| 2013 | Word2Vec | words as vectors (distributional meaning) |
| 2017 | "Attention Is All You Need" | the **Transformer** architecture |
| 2018 | BERT | **contextual** word representations |
| 2019 | T5 | **multi-task**: every task as text-to-text |
| 2020–23 | GPT | **scaling up** language models into LLMs |
| 2024 | reasoning models (GPT-4o, DeepSeek) | models that "think" before answering |
| 2025–26 | agents (Claude Code, Codex, Pi) | models that act with tools |

**Text as a universal representation (slide 16):**
- A **language model (LM)** predicts the **next word given a context**. It gives a probability
  distribution, e.g. after "I want to eat bread with", p("butter") = 0.12, p("jelly") = 0.03.
- A **neural LM** is a neural network trained to predict the next word.
- **Plain text is all you need to train**: there is no annotation cost. This is
  **semi-supervised (self-supervised) training**, and it removes the data era's bottleneck,
  expensive labels.
- **Autocomplete / generation:** predict the next token, add it to the context, repeat.
- **Pipeline (slide 15):** text → **tokenizer** → **trained encoder** → **vector
  representation** → model.

**From next-word prediction to multi-task models (slides 17–18):**
- Source: Sanh et al., *Multitask Prompted Training Enables Zero-Shot Task Generalization*
  (ICLR 2022, the **T0** model).
- Format **many tasks as text-to-text** transformations (a *prompt* describes the task) and
  train on that uniform format.
- The model then **generalizes to new task descriptions it never saw**. This is **zero-shot
  task generalization**, and **instruction fine-tuning** is what enables it.

**The three training stages (slide 19):**
1. **Pre-training:** "a college education", learning from vast data.
2. **Fine-tuning:** "specialising for your industry".
3. **Alignment:** "teaching it to behave": helpful and safe.

**Pre-training vs post-training (slide 20):**

| | Pre-training | Post-training |
|---|---|---|
| What | next-token prediction on a huge corpus (~1 TB of text) | **instruction fine-tuning** + **preference alignment** (RL) |
| Scale | trillions of tokens | thousands of examples |
| Cost | $10–100 M | $10–100 K |
| Result | a **"lossy zip of the internet"**: knowledge stored in the weights (**parametric memory**) up to a **training cutoff date** | a conversational, stylistically aligned chat assistant |

**Summary of slide 21. A foundation model is:**
1. a large trained neural network, characterised by its **number of parameters** and its
   **architecture (transformers)**;
2. trained on a **universal data representation**: the **input is a context** (a sequence of
   tokens) and the **output is a distribution over tokens**, iterated to generate text;
3. capable of **multi-task generalization through a task description**;
4. a **key component of a larger AI system**, not the whole system.

**How FMs are built:** semi-supervised pre-training on next-token prediction, then
post-training by instruction fine-tuning and preference alignment with RL.

## 4. Using foundation models (slides 22–27)

**Three usage patterns (slide 22):**
1. **Prompting:** use the model as is, with instructions and examples in the prompt.
2. **Fine-tuning:** train it further on your own data.
3. **Reinforcement learning:** shape its behaviour with rewards or preferences.

Slides 1–27 go into prompting. Fine-tuning starts at slide 29, outside this quiz.

**Types (slide 23):**

| Type | Use |
|---|---|
| **LLMs** (language) | chatbots, writing |
| **VLMs** (vision-language) | describing images, creating ads |
| **LRMs** (reasoning) | solving problems, analysing data |
| **World models** | predicting trends (weather, markets) |
| **Robotic models** | guiding robots |
| **Biological models** | trained on protein sequences |

- **Proprietary services:** ChatGPT, Claude, Grok, Gemini.
- **Open-access models:** Llama (Meta), DeepSeek, Mistral, Qwen (Alibaba), Muse.

**Selecting a model (slide 24):**
- **Performance:** leaderboards (LM Arena Elo score, Scale). Beyond one model, **system
  performance**: a *holistic benchmark* evaluates modular programs made of several LLMs.
- **Cost:**
  - *proprietary:* usage tier, licence, **price per input/output token**, latency;
  - *open:* run it in-house (privacy, but complex infrastructure) or through managed cloud
    services (e.g. Nebius, OpenRouter).

**Prompting basics (slides 25–26):**
- The LLM **predicts** the best answer to what you ask.
- **Temperature** trades creativity and diversity against precision.
- **Zero-shot:** ask it cold, with no examples.
- **Few-shot / in-context learning (ICL):** show examples in the prompt first. The model
  "learns" from the context without any training.
- **Chain of thought (CoT):** ask it to think step by step.
- **Conversation (chat):** multi-turn, where earlier turns are context.
- **Context:** the conversation plus working memory, read through the **attention mechanism**.
  More context gives better answers, up to a **limit**, and **large context costs more**.
- **Programmatic API:** a prompt goes in, text comes out, called from code.
- **Takeaway:** "How you ask matters as much as what you ask."

**Prompting costs and methodology (slide 27), very relevant to the course:**
- **Prompt selection is sensitive:** a **small change in the prompt can cause a large change in
  the outcome**.
- **Few-shot means choosing examples**, which is itself a design problem.
- **Prompt generation:** ask an AI to write the prompt.
- **Prompt optimization:** e.g. **DSPy**, which we did in the W3 lab.
- **Answer parsing:** extract the expected answer from free text, or drive the output to be
  **semi-structured (JSON, XML)** so it is easy to extract.
- **Benchmarking:** prepare test data, define an **evaluation metric**, and make evaluation
  **repeatable** as the data and the LLM version change.

---

# Part B: last week's lab (W2: specifications)

Full notes: [`../W2/PRACTICE.md`](../W2/PRACTICE.md) · summary:
[`../W2/TAKEAWAYS.md`](../W2/TAKEAWAYS.md)

**The lab preparation:** install OpenSpec and critique a deliberately weak spec. For each
problem, say what a coding agent would have to **guess** and what goes wrong. The categories
were:
- **ambiguity** ("the right category", "important issues");
- **incompleteness** (no schema, no SLA values);
- **inconsistency** (two rules for the same issue);
- **untestability** ("accurately", "fast and secure");
- **design-in-requirements** ("use GPT-4 with temperature 0 and a regex parser");
- **missing non-functional concern** (no security or latency target).

**The input:** change request **CR-1**: send security reports to a private queue, escalate them,
handle within 24 h, detect them with the model, and an existing `security` label counts. It
looked small and wasn't.

## Concepts to know

| Concept | Meaning |
|---|---|
| **Need vs requirement vs design decision** | a problem in the world → an observable property the system must have → how we chose to build it |
| **FR / quality attribute / constraint** | what it does / how well it does it / an imposed limit |
| **SRS (ISO/IEC/IEEE 29148)** | numbered requirements, each with a priority and a **verification method**, definitions, traceability |
| **29148 characteristics** | necessary, unambiguous, singular, feasible, verifiable, consistent, complete |
| **User story** | *As a ⟨role⟩, I want ⟨goal⟩, so that ⟨benefit⟩*, plus acceptance criteria |
| **INVEST** | Independent, Negotiable, Valuable, Estimable, Small, Testable |
| **Given/When/Then** | acceptance criteria written as concrete examples |
| **Traceability** | the links story ↔ requirement ↔ test (coverage and impact analysis) |
| **OpenSpec** | spec-driven development: a **change** = `proposal.md` (why) + **delta specs** (ADDED / MODIFIED / REMOVED requirements, each with `#### Scenario:`) + tasks |
| **`validate` / `archive`** | `validate` checks **structure**; `archive` merges deltas into the main spec and **drops** the why, design and quality targets |
| **MODIFIED requirement** | **replaces the whole block**, so copy it in full or you delete rules |
| **Domain model** | a **glossary** (one meaning per term, the ubiquitous language) plus **invariants** ("for every issue, …") |
| **Agent test** | ask what a coding agent would still have to **guess** |

## What happened in the three cycles
1. **User stories:**
   - US-06's weakest letter is **I** (it depends on another story);
   - US-08's weakest letter is **T** (you can't prove "can't steer routing");
   - CR-1 failed **S**, so we split it into 3 stories and 5 existing stories changed;
   - an agent would still have to guess 9 things.
2. **OpenSpec:** the lecturer's example failed validation (a missing scenario). Our change
   passed. **Validate caught** a dropped scenario, but **missed** a wrong requirement name and
   can't judge policy.
3. **Combining changes:** three changes that each passed validation produced contradictions:
   - a security bug could go to a public queue;
   - an SLA that depended on live 👍 counts, making routing non-deterministic;
   - `"Routing"` ≠ `router`;
   - a failure with a security label had no SLA.

   The fix is a domain model.

## Lessons
1. A **valid** spec isn't a **correct** spec. Tools check form; people check meaning.
2. Changes that are each valid can combine into an invalid system.
3. One term, one meaning.
4. Routing must be **deterministic**.
5. Small requests hide big changes.
6. **With agents, the spec is executed**: every gap becomes a guess.

---

# Part C: how the lecture and the lab connect (likely quiz material)

| Lecture idea | Where it showed up in the labs |
|---|---|
| ML is **probabilistic**: different answers to the same input | W1: we had to validate every model output; W2: **routing** must stay deterministic, with the model only extracting |
| **Biases** from the training distribution / data drift | W1: confidence about 1.0 even when wrong; W3: the agent used **stale memory** of a repo (a training cutoff) |
| **Lossy zip / parametric memory with a cutoff date** | the model "remembered" paths that no longer exist (`contrib/`, `src/...`) |
| **Few-shot = choosing examples** | W3: hand-picked example vs the optimizer's picks |
| **Answer parsing → structured output** | W1/W3: `Literal` types and a Pydantic `TriageRecord` |
| **Small prompt change → big outcome change** | specs and prompts are "executed": wording decides behaviour |
| **Benchmarking: test data, metric, repeatable** | the sealed `test.json`, the dev/train splits, `w3_results.json` |
| **FM is a component of a larger system** | the triage pipeline: LLM extraction + validation + deterministic routing |

---

# Practice questions

**1.** Name the three factors that made modern AI possible now.
<details><summary>Answer</summary>Better algorithms and ML understanding, the availability of data, and more computing power and storage.</details>

**2.** How does building a real-estate appraiser differ between classical software and ML?
<details><summary>Answer</summary>Classical: an expert and a product manager design a deterministic algorithm and data model by hand. ML: collect a dataset of features → prices, and a generic learning algorithm trains a model that memorizes and generalizes. The knowledge comes from data, not code.</details>

**3.** List the four characteristics of ML systems from the lecture.
<details><summary>Answer</summary>Probabilistic (different answers to the same input); uncertainty (it may answer with low confidence, or not know); biases from the training-data distribution (a train/inference mismatch gives unpredictable bias); and the most likely answer is not always the best action.</details>

**4.** Why was "plain text is all you need" a breakthrough?
<details><summary>Answer</summary>Next-word prediction needs no human labels: the next word *is* the label. That is self- or semi-supervised training, which removed the expensive annotation bottleneck of the data era and allowed training on internet-scale text.</details>

**5.** What is a language model? Give the output for a context.
<details><summary>Answer</summary>A model that gives a probability distribution over the next token given a context, e.g. p(butter | "I want to eat bread with") = 0.12. Generation repeats it: pick a token, append it, predict again.</details>

**6.** Pre-training vs post-training: data, scale, cost and result.
<details><summary>Answer</summary>Pre-training: next-token prediction on trillions of tokens (~1 TB), $10–100 M, giving a "lossy zip of the internet" with parametric memory up to a cutoff date. Post-training: instruction fine-tuning plus preference alignment (RL) on thousands of examples, $10–100 K, giving a helpful, aligned chat assistant.</details>

**7.** What does "multi-task generalization through task description" mean, and what enables it?
<details><summary>Answer</summary>Many tasks are formatted as text-to-text with a prompt describing the task; trained this way (instruction fine-tuning), the model can do *new* tasks from their description alone, i.e. zero-shot (T5, T0).</details>

**8.** Zero-shot vs few-shot vs chain of thought.
<details><summary>Answer</summary>Zero-shot: just the question or instruction. Few-shot (in-context learning): examples in the prompt first. Chain of thought: ask the model to reason step by step before answering.</details>

**9.** What does temperature control?
<details><summary>Answer</summary>The randomness of sampling: higher means more diverse and creative, lower means more precise and repeatable.</details>

**10.** Why is "more context = better answers" limited?
<details><summary>Answer</summary>The context window has a maximum size (like working memory), and large contexts cost more (tokens, money, latency). Attention over very long contexts is also less reliable.</details>

**11.** Give three methodological costs of prompting (slide 27).
<details><summary>Answer</summary>Any three: prompt sensitivity (a small delta gives a large outcome delta); choosing few-shot examples; answer parsing (often forcing JSON or XML); building a benchmark (test data, a metric, repeatable evaluation across data and model versions). Prompt optimization tools like DSPy address some of these.</details>

**12.** How would you choose a foundation model?
<details><summary>Answer</summary>Performance (leaderboards like LM Arena or Scale, plus system-level benchmarks for your task) and cost (proprietary: tier, licence, price per input/output token, latency; open: in-house deployment for privacy, or a managed cloud).</details>

**13.** Why is a foundation model "a component of a larger AI system"?
<details><summary>Answer</summary>On its own it only maps a context to a token distribution. A useful system adds input preparation, output parsing and validation, tools, deterministic logic and evaluation, like our triage pipeline (LLM extraction → TriageRecord validation → rule-based routing).</details>

**14.** (W2) What does INVEST stand for, and which letter did CR-1 fail?
<details><summary>Answer</summary>Independent, Negotiable, Valuable, Estimable, Small, Testable. It failed Small, so it was split into three stories (routing, model detection, label override).</details>

**15.** (W2) Three OpenSpec changes all pass `validate --strict`. Can the merged system still be wrong? Why?
<details><summary>Answer</summary>Yes. Each is validated against today's spec, not against the others. One silently removed the "unless overridden" clause another relied on, and two modified the same requirement. Validation checks form, not meaning.</details>

**16.** (W2) What does `openspec archive` keep and drop?
<details><summary>Answer</summary>It keeps requirements and scenarios in the main spec. It drops the proposal (why), the design and open questions, the tasks and the non-functional targets, which remain only in the archive folder.</details>

**17.** (W2) What is a domain model, and what problem does it solve?
<details><summary>Answer</summary>A glossary (one meaning per term) plus invariants that must hold for every issue. It catches vocabulary drift ("critical", "priority", "component" with two meanings) and conflicts between changes.</details>

**18.** (Link) Why does an LLM's training cutoff matter for an agent working on a code repository?
<details><summary>Answer</summary>Its knowledge is parametric memory up to the cutoff, a lossy zip. It may "remember" structure that has since changed (our ReAct agent looked for a `contrib/` folder that no longer exists). You give it current context with tools or retrieval instead of trusting its memory.</details>
