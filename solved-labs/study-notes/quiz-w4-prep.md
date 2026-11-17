# Quiz W4 prep

**Scope:** `LLMs/` notes, with the focus on **01 tokenization**, **02 next-token prediction**,
**03 decoding** (+ the Hugging Face post), **06 prompting strategies** and **06.5 RAG**. Short
recaps of 02.5, 04 and 05, plus the **DSPy** essentials. Q&A at the end.

```
text ─encode─► token IDs ─LM─► p(next token) ─decoding─► token ─repeat until [EOS]─► decode ─► text
```

---

## 1. Tokenization (01)

**Tokenization:** the first step of an LLM. It breaks raw text into **tokens**, and the LLM works
**only on tokens**.

**Tokenizer:** a function **string → list of integers** (token IDs).

| | Input | Output |
|---|---|---|
| **Encode** | a string | a list of token IDs |
| **Decode** | a list of token IDs | the string |

Each ID is looked up in the **embedding table** to get a vector.

**Why tokenize:**
1. **Numerical conversion:** the network needs numbers (IDs → embedding vectors).
2. **Vocabulary management:** a manageable vocabulary size instead of every word.
3. **Unknown words (OOV):** rare or new words are split into known sub-units, never `<UNK>`.

| Concept | Meaning |
|---|---|
| **Vocabulary size V** | the number of unique tokens (~30k–100k+); bigger V = fewer tokens but a bigger model |
| **Context length L** | the maximum tokens processed at once; longer input is **truncated** |
| **Objective** | the **fewest tokens** for the text, with vocabulary ≤ V: faster, cheaper, more fits |
| **Invertible + deterministic** | Detokenize(Tokenize(s)) = s and Tokenize(Detokenize(t)) = t |
| **Sub-word** | inflections (learn-ing), composites (micro+processor), OOV (Kuber+net+es) |
| **BPE** | start from characters → **merge the most frequent adjacent pair** → repeat until size V |

*BPE example:* `e`+`s` → `es`, then `es`+`t` → `est`. `lowering` → l o w er i n g. Text is first
split at spaces with regexps.

## 2. Next-token prediction (02)

| Concept | Meaning |
|---|---|
| **Language model** | p(tₙ \| t₀…tₙ₋₁): a probability for every vocabulary token being next |
| **Generative model** | by the chain rule the LM gives a distribution over **all sequences** |
| **Training** | maximize Σ log p(uᵢ \| previous k tokens): **cross-entropy**; k = the context window |
| **Perplexity** | the evaluation metric: uncertainty on a test corpus (lower = better) |
| **n-grams** | the old LMs (1970s–2000s), counting short sequences |
| **Bengio 2000** | learn a **distributed representation (vector) per word** + the probability function; similar words → nearby vectors → unseen sentences still work (beats the **curse of dimensionality**) |
| **GPT** | h₀ = token emb (Wₑ) + position emb (Wₚ) → n transformer blocks → **softmax** over V |

**02.5 Transformer recap:**
- **self-attention** = each token becomes a weighted mix of all tokens, softmax(QKᵀ/√d_k)·V;
- **positional embeddings** (RoPE) add word order;
- **block** = attention → layer norm → feed-forward → residual.

## 3. Decoding strategies (03 + Hugging Face "How to generate")

**Auto-regressive generation:** choose a token, append it, predict again, until **[EOS]**. The
**decoding strategy** decides *which* token to take from the distribution.

| Strategy | Meaning | Key point |
|---|---|---|
| **Greedy** | the highest-probability token each step | not the most probable **sequence**; repetitive |
| **Beam search** (`num_beams`) | keep the most likely sequences | good for predictable length (translation, summarization); dull for open-ended text |
| **n-gram penalty** (`no_repeat_ngram_size`) | forbid repeating an n-gram | blunt: "New York" only once |
| **Sampling** (`do_sample`) | random by probability | varied, but can be incoherent |
| **Temperature** | low = sharper, high = flatter | → 0 = greedy |
| **Top-k** | sample among the k most likely | k is fixed, doesn't adapt |
| **Top-p (nucleus)** | the smallest set with cumulative probability > p | **adapts** to the distribution |

**The Hugging Face conclusion:**
- **top-k and top-p are more fluent** for open-ended text;
- repetition is caused mainly by **how the model was trained**;
- **there is no one-size-fits-all method**.

**Other points:**
- **Degeneration** (Holtzman): maximizing likelihood gives **bland, repetitive** text, which is
  why nucleus sampling cuts the tail.
- **Speculative decoding:** a small model drafts and the big model verifies in parallel: faster,
  **identical output**.
- APIs usually expose **temperature and top-p**.
- Sampling means the **same prompt can give different outputs**.

## 4. Training recap (04, 05)

| Concept | Meaning |
|---|---|
| **Pre-training** | **self-supervised** (no labels): next-token prediction on huge raw text |
| **Fine-tuning** | supervised training on a small labelled set; 100 examples ≈ 10,000 from scratch |
| **T5 text-to-text** | every task as text with a task prefix: one loss, many tasks |
| **LoRA** | freeze the base model, train small low-rank matrices (W + B×A); cheap, no forgetting |
| **Instruction fine-tuning** | tasks phrased as instructions (FLAN) → **zero-shot on unseen tasks** |
| **4 stages** | **pre-training → SFT** (instruction, answer) **→ RLHF** (reward model + PPO) **→ reasoning RL** |

---

## 5. Prompting strategies (06)

**A prompting strategy** is an algorithm used **at inference time**, with **no training and no
weight updates**. It decides:
- how to encode the task into prompts;
- which sampling parameters to use;
- how to compute the final answer.

| Concept | Meaning |
|---|---|
| **Zero / one / few-shot** | 0 / 1 / a few examples in the prompt |
| **In-context learning (ICL)** | the model learns from prompt examples **without weight updates** |
| **Example choice and order** | strongly affect performance, so use **prompt optimization** |
| **What drives ICL** (Min 2022) | not correct labels, but the **label space, the input distribution, the format** |

**Why one prompt isn't enough:**
- the cost of generating is **O((P + A)²)**, because attention is quadratic;
- a complex task needs more computation, so it is **decomposed into steps**.

| Strategy | Meaning |
|---|---|
| **Chain of Thought (CoT)** | generate **intermediate reasoning steps** ("step by step"); emerges in large models |
| **Scratchpad** | write intermediate computations (the precursor of CoT) |
| **Program of Thought (PoT)** | generate a **program** and execute it externally; separates computation from reasoning (+12% vs CoT) |
| **Successive prompting / ReAct** | **interleave reasoning and actions** (tool calls) over turns; reduces hallucination |
| **Self-consistency** | sample **many reasoning paths** → take the **majority answer** |
| **Verification** | check answers (a verifier model, or a calculator for arithmetic) |
| **Tool use** | the LLM detects that a tool is needed, picks it and its parameters, merges the result |
| **Toolformer** | an LM that teaches itself which API to call, when and how |
| **MCP** | Anthropic's standard protocol to share and discover tools |

**In software engineering:** CoT and PoT do the agent's **planning**; **tool invocation** is
central to agents.

## 6. RAG: Retrieval-Augmented Generation (06.5)

**RAG** adds **retrieved external documents to the prompt**, so the answer is **grounded** in
up-to-date facts.

**Why:**
- the LLM's **parametric memory** (knowledge in its weights) is **static and goes stale**;
- on private or recent information it **hallucinates** (fluent but false).

**Two phases:**
- **indexing** (offline): documents → chunks → embeddings → vector DB;
- **retrieval & generation** (online): query → embedding → top-k chunks → LLM → answer.

| Component | Role |
|---|---|
| **Knowledge base / vector DB** | stores the document embeddings (or a BM25 text index) |
| **Encoder** (embedding model) | turns chunks and the query into vectors |
| **Retriever** | finds the **top-k** chunks by **cosine similarity**; a **re-ranker** improves them |
| **Generator** (LLM) | query + chunks → a grounded answer |

| Risk | Meaning |
|---|---|
| **Lost in the middle** | relevant context buried in a long prompt is ignored |
| **Retrieval noise** | irrelevant chunks: garbage in, garbage out |
| **Prompt injection** | malicious text tricks the model, e.g. into leaking private context |
| **Latency** | the extra retrieval step is slower |

| Metric | Meaning |
|---|---|
| **Precision@k / Recall@k** | the quality of the retrieved set |
| **MRR / nDCG** | the quality of the ranking |
| **Faithfulness (groundedness)** | the answer is supported by the retrieved context |
| **Answer relevance** | the answer addresses the query (often judged by an LLM) |

**Advanced RAG:** semantic chunking, HyDE, re-ranking, Graph RAG, **Self-RAG** (the LLM decides
when to retrieve).

---

## 7. DSPy essentials

**The idea:** you **declare** what a model call takes in and gives back, and DSPy writes the
prompt, calls the model, and parses the reply.

| Concept | Meaning |
|---|---|
| **`dspy.LM` + `dspy.configure`** | connect to a model (via LiteLLM) and make it the default |
| **Signature** | a class declaring typed **input and output fields**; its **docstring is the instruction** |
| **`Literal` output types** | the contract: only allowed values are accepted |
| **`dspy.Predict`** | runs one Signature as one LLM call and returns a `Prediction` |
| **`dspy.ChainOfThought`** | like Predict, but first asks for reasoning (CoT) |
| **`dspy.Example` + `.demos`** | few-shot examples, added to the prompt as earlier turns |
| **`dspy.Module` + `forward()`** | a program of several steps (calls, tools, `if`s) |
| **Tool** | a Python function; the model sees its name, type hints and docstring |
| **`dspy.ReAct`** | an agent loop: thought → tool call → observation, up to `max_iters` |
| **Optimizer (`BootstrapFewShot`)** | picks demos automatically from a train set using a **metric** |
| **`inspect_history`** | shows the exact prompt and reply |
| **Cache** | identical calls are served from cache, so reruns are cheap |

How it maps to the lecture: Signature = structured output; demos = few-shot / ICL; ChainOfThought
= CoT; ReAct = ReAct; optimizers = prompt optimization; Module + retriever = RAG.

---

## Practice Q&A

1. What are the input and output of a tokenizer?<details><summary>Answer</summary>Encode: a string → a list of integer token IDs. Decode: token IDs → the string.</details>
2. Why do LLMs need tokenization?<details><summary>Answer</summary>To turn text into numbers (IDs → embeddings), to keep the vocabulary a manageable size, and to handle unknown words by splitting them into known sub-units.</details>
3. What does a good tokenizer optimise, and what constraint must it satisfy?<details><summary>Answer</summary>The fewest tokens for a vocabulary of at most V; it must be invertible and deterministic: decode(encode(s)) = s.</details>
4. How does BPE build its vocabulary?<details><summary>Answer</summary>Start from characters and repeatedly merge the most frequent adjacent pair into a new token until the vocabulary reaches V.</details>
5. What does a language model compute, and how is it evaluated?<details><summary>Answer</summary>p(next token | previous tokens), a distribution over the vocabulary. It is trained with cross-entropy and evaluated with perplexity (lower = better).</details>
6. What was Bengio's key idea?<details><summary>Answer</summary>Learn a vector per word together with the probability function (representation learning), so unseen sentences of similar words still get high probability.</details>
7. What is auto-regressive generation?<details><summary>Answer</summary>Pick a token, append it to the input, predict the next, and repeat until [EOS].</details>
8. Greedy vs beam search: what is greedy's weakness?<details><summary>Answer</summary>Greedy picks the best token each step, not the best sequence. Beam search keeps the num_beams best sequences; both tend to repeat.</details>
9. Top-k vs top-p?<details><summary>Answer</summary>Top-k samples among the k most likely tokens (fixed). Top-p samples from the smallest set whose cumulative probability exceeds p, so it adapts.</details>
10. What does temperature do?<details><summary>Answer</summary>Low = a sharper distribution (more predictable); high = flatter (more diverse); near 0 = greedy.</details>
11. What did the Hugging Face post conclude?<details><summary>Answer</summary>Top-k and top-p are more fluent for open-ended text; repetition comes mostly from training; there is no one-size-fits-all method.</details>
12. What is a prompting strategy?<details><summary>Answer</summary>An inference-time algorithm (no weight updates) that decides how to encode the task into prompts, which sampling to use, and how to compute the answer.</details>
13. What is in-context learning?<details><summary>Answer</summary>Learning a task from examples in the prompt at inference time, without weight updates. Example choice and order matter; correct labels matter less than the format and label space.</details>
14. Why decompose complex tasks instead of using one prompt?<details><summary>Answer</summary>Generation costs O((P+A)²); a complex task needs more computation than one pass gives, so it is split into steps (CoT, PoT, ReAct, tools).</details>
15. CoT vs PoT vs ReAct?<details><summary>Answer</summary>CoT writes reasoning steps; PoT writes a program that is executed externally; ReAct interleaves reasoning with tool actions.</details>
16. What is self-consistency?<details><summary>Answer</summary>Sample several reasoning paths and take the majority answer.</details>
17. What problem does RAG solve?<details><summary>Answer</summary>Parametric memory is static and stale, so the LLM hallucinates on private or recent data. RAG retrieves documents into the prompt to ground the answer.</details>
18. Describe RAG's two phases and components.<details><summary>Answer</summary>Indexing (chunks → embeddings → vector DB) and retrieval & generation (query embedding → top-k by cosine similarity → LLM). Components: knowledge base, encoder, retriever (+ re-ranker), generator.</details>
19. Name two RAG risks and two RAG metrics.<details><summary>Answer</summary>Risks: lost in the middle, retrieval noise, prompt injection, latency. Metrics: Precision@k / Recall@k, MRR / nDCG, faithfulness, answer relevance.</details>
20. In DSPy, what is a Signature, and what does Predict do?<details><summary>Answer</summary>A Signature declares typed inputs and outputs, with the docstring as the instruction; Predict runs it as one LLM call and parses the reply.</details>
21. How does DSPy do few-shot and prompt optimization?<details><summary>Answer</summary>Few-shot: `dspy.Example` objects set as `.demos`. Optimization: an optimizer such as BootstrapFewShot picks demos from a train set using a metric.</details>
22. Module vs ReAct in DSPy?<details><summary>Answer</summary>In a Module your `forward()` code decides the steps and tool calls; in ReAct the model decides which tool to call in a thought → action → observation loop.</details>
