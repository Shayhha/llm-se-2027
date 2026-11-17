# Quiz W4 prep

**Scope:** the lecture notes in `LLMs/`: **01** tokenization, **02** next-token prediction,
**02.5** Transformers, **03** decoding (+ the Hugging Face post *How to generate text*), **04**
pre-training and fine-tuning, **05** post-training, **06** prompting strategies, **06.5** RAG.
Plus lab 4 (git), provisional until the lab is published.

```
text ─encode─► token IDs ─LM─► p(next token) ─decoding─► token ─append, repeat until [EOS]─► decode ─► text
```

---

## 1. Tokenization (file 01)

**Definition.** Tokenization is the critical first step in an LLM's workflow: breaking raw text
into smaller units called **tokens**. The LLM operates **exclusively on tokens**, not on the raw
characters or words.

**A tokenizer is a function that maps a string of text to a list of integers.**

| | Input | Output |
|---|---|---|
| **Tokenize / encode** | a string of text | a list of integers (token IDs) |
| **Detokenize / decode** | a list of token IDs | the string |

**Why tokenization is needed** (the LLM's vocabulary is fixed):
1. **Numerical conversion:** LLMs process numerical vectors. Tokens turn unstructured text into a
   sequence of discrete integers (IDs), which are mapped to **embedding vectors**.
2. **Vocabulary management:** a word-based vocabulary would need hundreds of thousands of entries
   (every word, proper noun and variant). Tokenization keeps the vocabulary size manageable, even
   across many languages.
3. **Handling unknown words (out-of-vocabulary):** by breaking words into sub-units, the model can
   still give meaning to rare or new words (e.g. "untokenizeable").

**Key parameters:**
- **Vocabulary size V:** the number of unique tokens. It is a hyper-parameter, about 30,000 to
  100,000+. A larger V represents common words with one token, but increases model size and
  training complexity.
- **Maximum context length L:** the maximum number of tokens processed at once (4096, 8192, …).
  Longer input is **truncated**.

**The objective (a good tokenizer):** a **short sequence of tokens that is still semantically
rich**:

`minimize Σᵢ Tokens(Sentenceᵢ)` subject to `VocabularySize ≤ V`

That is, **use the fewest tokens to represent the text, given a fixed vocabulary size.** Shorter
sequences mean faster inference, lower cost, and a larger effective context window.

**Constraint: invertible and deterministic.**
- `Detokenize(Tokenize(string)) == string`
- `Tokenize(Detokenize(tokens)) == tokens`

**Why sub-word tokenization** (units smaller than a word, larger than a character):
1. **Inflections:** "learning", "learns", "learned" share the root "learn", which keeps their
   semantic similarity.
2. **Composites:** compound or technical words split into known parts: "micro" + "processor".
3. **Out-of-vocabulary words:** "Kubernetes" → "Kuber" + "net" + "es", instead of `<UNK>`.

**Byte Pair Encoding (BPE):** the most popular sub-word algorithm (used in GPT-3). It is an
**iterative data-compression algorithm** that learns a vocabulary from the training corpus:
1. **Initialization:** the vocabulary is every unique character in the corpus.
2. **Iterative merging:** repeatedly find the **most frequent adjacent pair** and replace all its
   occurrences with a new single token.
3. **Stop** when the desired vocabulary size is reached, or no frequent pairs remain.

*Example.* Corpus `l o w e r` (5), `n e w e s t` (2), `w i d e s t` (3); the initial vocabulary is
the characters.
- Step 1: merge `e`+`s` → `es` (vocabulary +1).
- Step 2: merge `es`+`t` → `est` (vocabulary +1).
- A new word, `lowering` → `['l','o','w','er','i','n','g']` (if `er` was learned earlier).

In practice, the text is **first split into space-separated sequences using regular
expressions**, and BPE runs on each sequence.

---

## 2. Next-token prediction (file 02)

**The core of an LLM is a probabilistic function** mapping a set of tokens to a **distribution
over the possible next token**:

`LM: [t₀, …, tₙ₋₁] → p(tₙ | t<n)`

This prediction *is* the **language model**. By the **chain rule**,
`p(t₀, t₁, …, tₙ) = p(t₀) × p(t₁, …, tₙ | t₀)`, so it is equivalent to a distribution over
**all token sequences**. That is why an LM is a **generative model**.

**Training objective:** maximize the likelihood over a large corpus U:

`L₁(U) = Σᵢ log p(uᵢ | uᵢ₋ₖ, …, uᵢ₋₁; θ)`

Here **k is the context window**. This is the **cross-entropy loss**: the model should give a high
probability to the token actually observed. LMs are evaluated with **perplexity**, the
uncertainty in predicting the observed words of a test corpus (lower = better).

**History:** **n-gram methods** (1970s–2000s), then the **neural LM** of Bengio et al. (2000).

**Bengio's key concept, representation learning:**
- The difficulty is the **curse of dimensionality**: a test sequence is likely different from
  every training sequence.
- n-grams generalize by concatenating very short seen sequences.
- Bengio learns, **at the same time**, (1) a **distributed representation for each word** and
  (2) **the probability function for sequences, expressed in those representations**.
- An unseen sequence gets high probability **if its words are similar** (nearby representations)
  to words of a seen sentence. Each training sentence informs the model about an exponential
  number of semantically neighbouring sentences.

**LMs are better than humans at next-token prediction** (Shlegeris et al., TMLR 2024), even small
models such as GPT-3 Ada, measured by top-1 accuracy and perplexity.

**The Transformer** improved neural LMs dramatically over RNNs, LSTMs and GRUs. GPT uses a
multi-layer **transformer decoder** (notation of Radford et al., 2018):
- **Initial token embedding:** `h₀ = U·Wₑ + Wₚ`
- **Multi-layer transformation:** `hₗ = transformer_block(hₗ₋₁)` for l ∈ [1, n]
- **Final prediction:** `p(u) = softmax(hₙ·Wₑᵀ)`

where U = the last k context tokens, n = the number of layers, **Wₑ = the token embedding matrix**, **Wₚ = the position embedding matrix**.

**Softmax** turns a vector of size V into a distribution (values between 0 and 1, summing to 1).
All parameters are trained **end to end** on the LM objective.

---

## 3. Transformers (file 02.5)

From **Vaswani et al., NeurIPS 2017** ("Attention Is All You Need"). The initial embeddings can
come from a context-free method such as **Word2Vec or GloVe**.

**Positional embeddings (Wₚ):** **self-attention does not take word order into account**, so
without them the model couldn't distinguish the order of words. The forms are:
- **sinusoidal** (sine and cosine functions of varying frequencies);
- **learned** (trained with the model);
- **RoPE** (2021), the most common today.

**Attention** describes the **mutual influence of tokens** in the sequence: the representation of
each token is a **weighted combination of the representations of the neighbouring tokens**.
Learning attention means learning how to compute these influence weights.

**One transformer block:**
1. **Input embedding:** project the input into a higher-dimensional space.
2. **Multi-head self-attention:**
   - `Q = X·W_Q`, `K = X·W_K`, `V = X·W_V` (query, key, value)
   - `Attention(Q, K, V) = softmax(Q·Kᵀ / √d_k) · V`
   - the scaled dot product of Q and K gives the weights, applied to V.
3. **Layer normalization:** normalize to zero mean and unit variance.
4. **Feed-forward network:** two linear layers with a ReLU: `ReLU(X·W₁ + b₁)·W₂ + b₂`
5. **Residual connection:** add the block's input back, `X_out = X_norm + FF`, which preserves
   information.
6. **Final output:** a linear layer + softmax gives the probability distribution over the
   vocabulary.

---

## 4. Decoding strategies (file 03 + the Hugging Face post)

**Decoding:** an LM gives a distribution over the vocabulary for a prefix. To generate **text**,
tokens are produced in an **auto-regressive** manner: generate t₁ from the prefix, then t₂ from
(prefix, t₁), and so on, **until a special [EOS] (end-of-sequence) token**. The length isn't fixed
in advance.

| Method | How it works | Parameters | Weakness |
|---|---|---|---|
| **Greedy** | the highest-probability token at each step | default | not the highest-probability *sequence*: a likely first token can hide a better path; repetitive |
| **Beam search** | keeps the `num_beams` most likely sequences and returns the best | `num_beams`, `early_stopping` | at least as likely as greedy but not guaranteed optimal; still repetitive |
| **n-gram penalty** | sets to 0 the probability of any word that would repeat an n-gram | `no_repeat_ngram_size` | must be used carefully: "New York" could appear only once |
| **Sampling** | picks the next token **randomly according to its probability** | `do_sample=True` | non-deterministic; often incoherent |
| **Temperature** | lower → sharper distribution (likely tokens boosted) | `temperature` | → 0 becomes greedy |
| **Top-k** (Fan 2018) | samples among the **k most likely** tokens (used by GPT-2) | `top_k` (e.g. 50) | k is fixed: doesn't adapt to sharp or flat distributions |
| **Top-p / nucleus** (Holtzman 2019) | samples from the **smallest set whose cumulative probability exceeds p** | `top_p` (e.g. 0.92) | — adapts to the distribution |

- `num_return_sequences` returns several outputs. Top-k and top-p can be **combined**
  (`top_k=50, top_p=0.95`).
- **APIs usually expose** decoding parameters, most often **top-p and temperature**.

**Hugging Face arguments and conclusion:**
- Beam search works when the **output length is predictable** (translation, summarization), not
  for **open-ended** generation (dialogue, stories).
- **Human text does not follow the highest-probability words**: humans want to be surprised (Holtzman).
- **Conclusion:** for open-ended generation, **top-p and top-k produce more fluent text** than
  greedy or beam. The repetition is **caused by the model, especially the way it is trained**,
  rather than by the decoding method (Welleck). Top-k and top-p also repeat, and with an adapted
  training objective, beam search can be more fluent. **There is no one-size-fits-all
  method.**

**The research papers** in file 03:

| Paper | Main point |
|---|---|
| **Holtzman et al. 2020**, *Neural Text Degeneration* | likelihood as the *decoding* objective gives **bland, strangely repetitive** text; **nucleus sampling** cuts the unreliable **tail** of the distribution |
| **Meister et al. 2020**, *If beam search is the answer…* | exact MAP decoding is often poor; beam search works because it enforces **uniform information density** |
| **Choi et al. 2022**, *Non-monotonic self-terminating LM* | greedy, beam, top-k and nucleus can cause **non-termination, repetition, premature termination** |
| **Welleck et al. 2020**, *Unlikelihood training* | the **likelihood training objective** is at fault (too much probability on repeats and frequent words); train unlikely generations to lower probability |
| **Hewitt et al. 2022**, *Truncation as desmoothing* | top-k and top-p are "desmoothing"; top-p can cut good words; **η-sampling** uses an entropy-dependent threshold |
| **Leviathan et al. 2023**, *Speculative decoding* | K tokens need K serial runs; a **fast model drafts**, the large model verifies in parallel: **2–3× faster, identical outputs**; the main method in production |

---

## 5. Pre-training, fine-tuning, multi-task, instruction fine-tuning (file 04)

Current LLMs start from a transformer-based trained language model and add **further training
rounds**, with different techniques, data sources and objectives.

**Pre-training:** training the LM on **self-supervised tasks**, then re-using the pre-trained model
to solve **downstream tasks**.
- **Self-supervision** means text tasks that **need no manual annotation**, only observable text:
  next-word prediction, masked-word prediction, perturbation removal.
- Raw text is **abundant**; annotated data is **scarce and expensive**.
- These tasks still give surprisingly **general linguistic knowledge**.

**Fine-tuning:** training a pre-trained model in a **supervised (discriminative)** way on a
**relatively small labelled dataset** C of (x₁…xₘ, y).
- **Advantages over training from scratch:**
  - **less labelled data:** 100 examples fine-tuned ≈ 10,000 from scratch (Howard & Ruder 2018);
  - **one model, many tasks:** a multi-task model.
- **Adaptation techniques:** mixture models, adapters, frozen or updated pre-trained layers.
- **Radford et al. 2018:**
  - the last block's activation h feeds a new linear layer: `p(y | x) = softmax(h·W_y)`;
  - the task objective is `L₂(C) = Σ log P(y | x₁…xₘ)`;
  - fine-tuning optimizes the **mixture** `L₃(C) = L₂(C) + λ·L₁(C)`, the task loss plus
    next-word prediction.

**Multi-task models:**
- **ULMFiT** (2018): one model fine-tuned on 6 tasks, state of the art with **100× less data**.
- **T5** (Raffel 2020):
  - more and more varied tasks (GLUE, SuperGLUE, summarization, QA, translation);
  - a **uniform text-to-text format** with a **task-description prefix**, so there is **one
    cross-entropy loss for all tasks**; the prefix is the ancestor of prompting;
  - multi-task works **only beyond a certain scale**, of both parameters and data (the **C4**
    dataset, about 100× Wikipedia). T5-11B was state of the art on 26 tasks.
- **Task counts kept growing:** 6 (ULMFiT) → 25 (T5) → 60 (T0) → 1,600 (Super-NaturalInstructions)
  → 1,800 (FLAN) → **2,000** (OPT-IML).

**LoRA (Low-Rank Adaptation, 2021):** the **most common** fine-tuning method today. It is
**parameter-efficient fine-tuning (PEFT)**:
- **freeze** the original weights (which avoids **catastrophic forgetting**);
- **inject small trainable low-rank matrices** into some layers (e.g. self-attention);
- **train only them**;
- at inference: `W_original + B × A`.

Its benefits: **efficiency** (far fewer trainable parameters), **lower cost**, **performance**
comparable to full fine-tuning, **flexibility** (swap task adapters on one base model).

**Instruction fine-tuning** (**FLAN**, 2021; **InstructGPT**, OpenAI 2022):
- fine-tune on many tasks **described in natural-language instructions**, with data
  (task instruction, input, label);
- the model then **generalizes zero-shot to unseen tasks** described only by an instruction.
- **InstructGPT:** labeller demonstrations (supervised), then **rankings + RL from human feedback**.
  The 1.3B InstructGPT is **preferred over the 175B GPT-3**: bigger ≠ better at following intent.
- **FLAN scaling (Chung 2022):** scaling **tasks**, **model size** and **CoT data** all help.
  Super-NaturalInstructions: **the number of tasks helps more than model size**.

## 6. Post-training: the 4 stages of training an LLM (file 05)

Each stage **builds on the capabilities of the previous one**, to produce a model that is helpful,
harmless, and good at following instructions and reasoning.

| Stage | Objective | Method |
|---|---|---|
| **1. Pre-training** | a broad linguistic foundation and world knowledge | **self-supervised next-token prediction** on vast unlabelled text |
| **2. Instruction fine-tuning (SFT)** | follow instructions, converse; comply with format and style; bridges *next-word predictor → helpful assistant* | supervised training on curated **(instruction, ideal output)** pairs |
| **3. Alignment (RLHF)** | match human preferences and ethics: helpful, honest, less biased or harmful | **reward model** trained on human rankings of responses, then **RL fine-tuning (e.g. PPO)** to maximize the reward |
| **4. Reasoning RL** | complex **multi-step reasoning**, often with **process-based rewards** (on the reasoning steps) | advanced RL on reasoning benchmarks; **needed for CoT, tool use and PoT to work well** |

## 7. Prompting strategies (file 06)

**Definition:** given a fully trained LLM, prompting strategies are **algorithms used at inference
time**, with **no training and no weight updates**. They decide:
- how to **encode the task into one or more prompts**;
- which **sampling parameters** to use (see decoding);
- how to compute the **final answer**.

They are implemented as libraries that call an LLM API.

**Zero-shot / one-shot / few-shot:** zero, one, or a few examples in the prompt.

**In-context learning (ICL):** few-shot works **without any weight update**: the model "learns"
from the examples **at inference time**, unlike earlier machine learning.
- **The order and choice of examples strongly affect performance**, so set them with **prompt
  optimization** on a small training set.
- **What explains it:**
  - Garg 2022: Transformers can in-context learn function classes, e.g. linear functions;
  - Xie 2022: ICL as **implicit Bayesian inference** of a shared latent concept;
  - Min 2022: **correct labels are barely needed**; what matters is the **label space**, the
    **input distribution** and the **format**.

**Complex prompting: why one prompt isn't enough.**
- Generating an answer of length A from a prompt of length P costs `O((P + A)²)`, because
  **attention is quadratic in context length**.
- A task needing more computation than that is unlikely to be solved, **unless the answer grows
  with the task's complexity**.
- So we decompose the task:

| Strategy | How it works |
|---|---|
| **Chain solutions (CoT, PoT)** | the model generates the sequence of sub-steps at once |
| **Successive prompting (ReAct)** | alternate **question decomposition** and **question answering**; each step's history goes into the next prompt (multi-turn) |
| **Consistency / voting** | run the task several times (higher temperature for variety), compare the candidates, choose; optionally **verify** the answer with the LLM |
| **Tool support** | delegate sub-tasks to tools (calculator, logic solver, retriever or search); the LLM detects that a tool is needed, picks it, extracts its parameters, and merges the result into the context |

**The methods:**
- **Scratchpads** (Nye 2021): emit intermediate steps "step by step" to a scratchpad, which makes
  multi-step computation possible (long addition, running programs).
- **Chain of Thought, CoT** (Wei 2022): a few demonstrations with **intermediate reasoning steps**.
  - It **emerges in large models**: 540B with 8 CoT examples was state of the art on GSM8K.
  - Even **invalid reasoning** in the demos keeps 80–90% of the gain; **relevance and the order of
    the steps** matter more (Wang 2022).
- **Program of Thought, PoT** (Chen 2022): the LLM writes a **program**, and an external computer
  runs it. This **separates computation from reasoning**: about **+12% over CoT** on math and
  finance problems.
- **ReAct** (Yao 2023): **interleave reasoning traces and actions** (e.g. calls to a Wikipedia
  API).
  - Reasoning helps plan and handle exceptions; actions fetch outside information.
  - It **reduces hallucination and error propagation** compared with CoT, and its trajectories
    are interpretable.
- **Self-consistency** (Wang 2022): **sample many reasoning paths**, then take the **majority
  answer** instead of greedy decoding (+17.9% on GSM8K).
- **Verifiers** (Cobbe 2021): generate many solutions; a trained verifier picks the best (it scales
  better than fine-tuning). An **arithmetic verifier** checks the answer with a calculator.
- **Consistency** (Elazar 2021): models give **inconsistent answers to paraphrases** of the same
  question.
- **Toolformer** (Schick 2023): the LM **teaches itself** (self-supervised) **which API to call,
  when, with which arguments**, and how to use the result: calculator, QA, search, translation,
  calendar.

**For software engineering:**
- **CoT and PoT** do the **planning** in agents.
- **Tool invocation** is central to them.
- **MCP (Model Context Protocol, Anthropic)** standardizes how tools are shared and discovered.

## 8. RAG: Retrieval-Augmented Generation (file 06.5)

**RAG** gives the LLM access to **external, non-parametric knowledge** during generation, to
improve factual accuracy.

**Motivation:**
- **Memorization:** the LLM's internal knowledge, its **parametric memory**, is **static** and goes
  **stale**.
- On **domain-specific, private or very recent** information, an LLM **hallucinates** (fluent but
  false) or says it doesn't know.
- RAG **adds relevant retrieved documents to the prompt**, so the answer is **grounded** in
  up-to-date external facts.

**The pipeline:**
- **Indexing** (offline, data preparation);
- **Retrieval & generation** (online, at query time).

| Component | Role |
|---|---|
| **Knowledge base (corpus)** | the domain or private data: documents → **embeddings** in a **vector database** (or a classic IR index such as **BM25**) |
| **Encoder** (embedding model, e.g. Sentence Transformer) | turns chunks into vectors (indexing) and the **query** into a vector (retrieval) |
| **Retriever** | vector search for the **top-k** chunks by **cosine similarity**; an optional **re-ranker** improves the set |
| **Generator** (the LLM) | gets the query + the retrieved chunks and writes a **grounded** answer |

**Examples:** enterprise QA over internal documents, a customer-support bot with live data,
literature review of papers newer than the training cutoff.

**Advanced RAG:**
- **chunking:** semantic, recursive, metadata-aware;
- **retrieval optimization:** **HyDE**, re-ranking with cross-encoders, query expansion, **Graph
  RAG**;
- **end-to-end:** **Self-RAG**, where the LLM decides when and what to retrieve.

**Limitations and risks:**
- **Context overload / lost in the middle:** relevant context buried in a long prompt is ignored.
- **Retrieval noise:** garbage in, garbage out.
- **Security:** prompt injection and jailbreaks that leak private context; use guardrails.
- **Latency:** the extra retrieval step; use caching and faster indexes.

**Evaluation:**
- **Retrieval metrics:** **Precision@k, Recall@k**, and ranking quality with **MRR, nDCG**.
- **End-to-end metrics** (often **LLM-as-a-judge**):
  - **faithfulness / groundedness:** the answer is supported by the retrieved context;
  - **answer relevance:** it answers the query;
  - **context recall / relevance:** the chunks contain what's needed.
- **Frameworks:** RAGAs, ARES.

**Original paper:** Lewis et al., NeurIPS 2020: a seq2seq generator + **Dense Passage Retriever
(DPR)**. The course project will implement RAG with **DSPy**.

## 9. Lab 4: git internals (provisional, from the syllabus)

- **Content-addressed object store:** objects are named by the **hash of their content** and are
  immutable.
  - **blob** = file content
  - **tree** = directory (names → hashes)
  - **commit** = tree + parent(s) + message
- **The lab implements:**
  - `hash-object`: content → blob
  - `cat-file`: read an object
  - `write-tree`: index → tree
  - `commit-tree`: tree → commit
- **Refs** are mutable pointers (branches). **HEAD** is the current position. **Detached HEAD**
  points directly at a commit.
- **Recovery:** `git reflog` → `git reset --hard <hash>` restores commits lost by a botched
  rebase or reset.

---

## Concepts to memorize

| Concept | Meaning (as in the course notes) |
|---|---|
| **Tokenizer** | a function mapping a string to a list of integers |
| **Encode / decode** | tokenize: text → token IDs; detokenize: token IDs → text |
| **Vocabulary size V** | the number of unique tokens (a hyper-parameter, ~30k–100k+) |
| **Max context length L** | the maximum tokens processed at once; longer input is truncated |
| **Tokenizer objective** | the fewest tokens for the text, given vocabulary size ≤ V |
| **Sub-word tokenization** | units between characters and words: inflections, composites, OOV words |
| **BPE** | iterative compression: start from characters, merge the most frequent adjacent pair until size V |
| **Language model** | p(next token \| previous tokens); a distribution over sequences (chain rule) |
| **Likelihood / cross-entropy** | the training objective: high probability for the observed next token |
| **Perplexity** | the evaluation metric: uncertainty in predicting a test corpus |
| **Distributed representation** | a learned vector per word; similar words → nearby vectors |
| **Softmax** | turns a V-sized score vector into a probability distribution |
| **Positional embedding** | adds word order (sinusoidal, learned, RoPE) |
| **Self-attention** | each token = a weighted combination of the other tokens; softmax(QKᵀ/√d_k)V |
| **Auto-regressive** | generate token by token, feeding each back in, until [EOS] |
| **Greedy / beam search** | the top token each step / the top `num_beams` sequences |
| **Sampling / temperature** | random by probability / sharpen (low) or flatten (high) the distribution |
| **Top-k / top-p (nucleus)** | the k most likely tokens / the smallest set with cumulative probability > p |
| **Text degeneration** | bland, repetitive text from likelihood-maximizing decoding |
| **Speculative decoding** | a draft model plus parallel verification: faster, identical output |
| **Self-supervision** | training tasks needing no manual labels (next / masked word, perturbation removal) |
| **Fine-tuning** | supervised training of a pre-trained model on a small labelled dataset; L₃ = L₂ + λ·L₁ |
| **Multi-task / text-to-text (T5)** | one model, many tasks, each in a uniform text format with a task prefix |
| **LoRA / PEFT** | freeze the base weights, train small low-rank matrices: W + B×A |
| **Catastrophic forgetting** | losing old knowledge when retraining; LoRA avoids it by freezing |
| **Instruction fine-tuning (FLAN)** | train on many instruction-described tasks → zero-shot on unseen tasks |
| **SFT** | supervised fine-tuning on (instruction, ideal output) pairs |
| **RLHF** | a reward model trained on human rankings + RL (PPO) to maximize it |
| **Reasoning RL** | RL with process-based rewards for multi-step reasoning |
| **Prompting strategy** | an inference-time algorithm (no weight updates) for using an LLM on a task |
| **In-context learning (ICL)** | learning from prompt examples at inference time, without weight updates |
| **CoT / scratchpad** | prompt the model to produce intermediate reasoning steps |
| **PoT** | the model writes a program; executing it gives the answer |
| **ReAct** | interleaved reasoning and tool actions (successive prompting) |
| **Self-consistency** | sample many reasoning paths; take the majority answer |
| **Verifier** | a model or tool that checks candidate answers and picks the best |
| **Toolformer / MCP** | an LM that teaches itself to call APIs / a standard protocol for sharing tools |
| **RAG** | retrieve relevant documents and add them to the prompt, to ground the answer |
| **Parametric memory** | knowledge stored in the model's weights; static, goes stale |
| **Hallucination** | fluent but factually wrong output |
| **Embedding / vector DB** | the vector of a text chunk / the store searched by similarity |
| **Retriever / re-ranker** | finds the top-k chunks by cosine similarity / re-orders them by relevance |
| **Lost in the middle** | the LLM ignores relevant context buried in a long prompt |
| **Faithfulness (groundedness)** | the answer is supported by the retrieved context |
| **Precision@k / Recall@k / MRR / nDCG** | retrieval quality metrics (the set / its ranking) |
| **Blob / tree / commit / reflog** | git: file / directory / snapshot / history of HEAD for recovery |

---

## Practice Q&A

1. What are the input and output of a tokenizer?<details><summary>Answer</summary>A tokenizer maps a string of text to a list of integers (token IDs); detokenizing maps the IDs back to the string.</details>
2. Give the three reasons tokenization is needed.<details><summary>Answer</summary>Numerical conversion (IDs mapped to embedding vectors), vocabulary management (a manageable size), and handling unknown (out-of-vocabulary) words by breaking them into sub-units.</details>
3. State the tokenizer's objective and its constraint.<details><summary>Answer</summary>Minimize the total number of tokens subject to vocabulary size ≤ V. It must be invertible and deterministic: Detokenize(Tokenize(s)) = s and Tokenize(Detokenize(t)) = t.</details>
4. Why sub-word tokenization? Give the three reasons.<details><summary>Answer</summary>Inflections share a root (learn-ing/-s/-ed), composites split into known parts (micro+processor), and OOV words are split instead of becoming `<UNK>` (Kuber+net+es).</details>
5. Describe BPE and how `lowering` is tokenized.<details><summary>Answer</summary>Start from characters; repeatedly merge the most frequent adjacent pair into a new token until size V. `lowering` → l, o, w, er, i, n, g.</details>
6. Define a language model and explain why it is "generative".<details><summary>Answer</summary>p(tₙ | t<n), a distribution over the next token. By the chain rule it defines a distribution over all token sequences, so it is a generative model.</details>
7. What is the LM training objective and evaluation metric?<details><summary>Answer</summary>Maximize Σ log p(uᵢ | the previous k tokens), i.e. the cross-entropy loss. Evaluated with perplexity.</details>
8. What problem did Bengio et al. solve, and how?<details><summary>Answer</summary>The curse of dimensionality. Learn a distributed representation per word together with the sequence probability function, so unseen sentences of similar words get high probability.</details>
9. Why are positional embeddings needed, and which kinds exist?<details><summary>Answer</summary>Self-attention ignores order. The kinds are sinusoidal, learned, and RoPE (the most common).</details>
10. List the steps of a transformer block and the attention formula.<details><summary>Answer</summary>Multi-head self-attention softmax(QKᵀ/√d_k)V → layer norm → feed-forward (2 linear + ReLU) → residual connection; final linear + softmax.</details>
11. What is auto-regressive generation, and why isn't greedy optimal?<details><summary>Answer</summary>Generate a token, append it, predict the next, until [EOS]. Greedy picks the top token each step, which can hide a better overall sequence behind a lower-probability token.</details>
12. What did the Hugging Face post conclude?<details><summary>Answer</summary>Top-p and top-k produce more fluent open-ended text than greedy or beam; repetition is caused mainly by the model's training (Welleck); there is no one-size-fits-all decoding method.</details>
13. What is speculative decoding?<details><summary>Answer</summary>A fast model drafts tokens and the large model verifies them in parallel: 2–3× faster with identical outputs; the main method in production.</details>
14. What is self-supervision, and why is it the basis of pre-training?<details><summary>Answer</summary>Training tasks that need no manual labels, only raw text (next-word or masked-word prediction, perturbation removal). Raw text is abundant while labelled data is scarce and expensive, and these tasks still teach general linguistic knowledge.</details>
15. What are the two advantages of fine-tuning over training from scratch? Write the fine-tuning objective.<details><summary>Answer</summary>Good performance with far less labelled data (100 ≈ 10,000 examples), and one pre-trained model can be adapted to many tasks. L₃(C) = L₂(C) + λ·L₁(C): the task loss plus next-word prediction.</details>
16. What did T5 introduce?<details><summary>Answer</summary>A uniform text-to-text format for all tasks, with a task-description prefix, so one cross-entropy loss serves every task (the ancestor of prompting). It also showed that multi-task works only beyond a certain scale of model and data (C4).</details>
17. How does LoRA work, and why use it?<details><summary>Answer</summary>Freeze the base weights, inject small trainable low-rank matrices, train only those, and at inference use W + B×A. It is efficient and cheap, matches full fine-tuning, avoids catastrophic forgetting, and adapters can be swapped per task.</details>
18. What is instruction fine-tuning, and what does it enable?<details><summary>Answer</summary>Fine-tuning on many tasks phrased as natural-language instructions (FLAN, InstructGPT). The model then performs unseen tasks zero-shot from just their instruction.</details>
19. Name the 4 stages of training an LLM, each with its method.<details><summary>Answer</summary>Pre-training (self-supervised next-token prediction) → SFT ((instruction, ideal output) pairs) → RLHF (a reward model from human rankings + PPO) → reasoning RL (process-based rewards for multi-step reasoning).</details>
20. What is a prompting strategy?<details><summary>Answer</summary>An inference-time algorithm (no training or weight updates) that decides how to encode a task into prompts, which sampling parameters to use, and how to compute the final answer.</details>
21. What is in-context learning, and what affects it?<details><summary>Answer</summary>Learning a task from examples in the prompt at inference time, with no weight updates. The choice and order of the examples strongly affect it; correct labels matter less than the label space, the input distribution and the format (Min 2022).</details>
22. Why can a single prompt be too limited for complex tasks?<details><summary>Answer</summary>Generation costs O((P+A)²) because attention is quadratic; a task needing more computation than that can't be solved in one pass unless the answer grows with the task's complexity, so the task is decomposed.</details>
23. CoT vs PoT vs ReAct.<details><summary>Answer</summary>CoT: generate intermediate reasoning steps. PoT: generate a program that an external computer runs (separating computation from reasoning, +12% over CoT). ReAct: interleave reasoning with tool actions, which reduces hallucination.</details>
24. What is self-consistency?<details><summary>Answer</summary>Sample several reasoning paths (with temperature) and choose the majority answer, instead of greedy decoding.</details>
25. What problem does RAG solve, and how?<details><summary>Answer</summary>An LLM's parametric memory is static and stale, so it hallucinates on private or recent information. RAG retrieves relevant documents and adds them to the prompt, so the answer is grounded in external, up-to-date facts.</details>
26. Name RAG's two phases and four components.<details><summary>Answer</summary>Indexing (offline) and retrieval & generation (online). Components: knowledge base / vector DB, encoder (embedding model), retriever (top-k by cosine similarity, plus a re-ranker), generator (the LLM).</details>
27. Give two RAG risks and two evaluation metrics.<details><summary>Answer</summary>Risks: lost in the middle, retrieval noise, prompt injection, latency. Metrics: Precision@k / Recall@k, MRR / nDCG, faithfulness (groundedness), answer relevance.</details>
28. (Lab 4) Git's objects and how to recover lost commits.<details><summary>Answer</summary>Blob, tree and commit, named by content hash. `git reflog` → `git reset --hard <hash>`.</details>
