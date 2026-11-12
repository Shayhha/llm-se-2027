# Quiz W4 cheat sheet

`text ─encode─► token IDs ─LM─► p(next token) ─decoding─► token ─repeat until [EOS]─► decode ─► text`

## Tokenization (01)

| Concept | Meaning |
|---|---|
| **Tokenization** | the critical first step: break raw text into tokens; the LLM operates only on tokens |
| **Tokenizer** | a function mapping a string of text → a list of integers |
| **Encode / decode** | tokenize: text → token IDs; detokenize: token IDs → text |
| **Why** | (1) numerical conversion → embedding vectors; (2) a manageable vocabulary size; (3) handling unknown (OOV) words |
| **Vocabulary size V** | the number of unique tokens; a hyper-parameter, ~30k–100k+; bigger = common words in 1 token, but a bigger model |
| **Max context length L** | the maximum tokens at once (4096, 8192, …); longer input is truncated |
| **Objective** | minimize Σ Tokens(Sentenceᵢ) subject to VocabularySize ≤ V: the fewest tokens, still semantically rich |
| **Constraint** | invertible + deterministic: Detokenize(Tokenize(s)) = s; Tokenize(Detokenize(t)) = t |
| **Sub-word** | inflections (learn-ing), composites (micro+processor), OOV (Kuber+net+es instead of `<UNK>`) |
| **BPE** | iterative compression: start from characters → merge the most frequent adjacent pair → until size V (used in GPT-3) |
| **BPE example** | `e`+`s` → `es`, then `es`+`t` → `est`; `lowering` → l o w er i n g |
| **Pre-split** | text is first split into space-separated sequences with regexps |

## Language model (02)

| Concept | Meaning |
|---|---|
| **LM** | a probabilistic function [t₀…tₙ₋₁] → p(tₙ \| t<n): a distribution over the next token |
| **Chain rule** | p(t₀…tₙ) = p(t₀)·p(t₁…tₙ \| t₀), so a distribution over all sequences: a **generative model** |
| **Objective** | L₁(U) = Σ log p(uᵢ \| uᵢ₋ₖ…uᵢ₋₁; θ), with k = context window: **cross-entropy** |
| **Perplexity** | the evaluation metric: uncertainty in predicting a test corpus (lower = better) |
| **n-grams** | the classic LMs (1970s–2000s); generalize by concatenating short seen sequences |
| **Bengio 2000** | fight the **curse of dimensionality** by learning a **distributed representation** per word together with the sequence probability function |
| **Representation learning** | similar words → nearby vectors, so unseen sentences of similar words get high probability |
| **Better than humans** | LMs beat humans at next-token prediction (top-1 accuracy, perplexity) |
| **GPT equations** | h₀ = U·Wₑ + Wₚ → hₗ = transformer_block(hₗ₋₁) → p(u) = softmax(hₙ·Wₑᵀ) |
| **Wₑ / Wₚ / softmax** | token embedding matrix / position embedding matrix / V scores → a probability distribution |

## Transformer (02.5)

| Concept | Meaning |
|---|---|
| **Transformer** | Vaswani et al. 2017; replaced RNNs, LSTMs, GRUs |
| **Positional embeddings** | needed because self-attention ignores order: sinusoidal, learned, **RoPE** (most common) |
| **Attention** | the mutual influence of tokens: each token = a weighted combination of its neighbours |
| **Self-attention formula** | Q = XW_Q, K = XW_K, V = XW_V; softmax(QKᵀ/√d_k)·V; **multi-head** = several in parallel |
| **Block** | attention → layer norm (zero mean, unit variance) → feed-forward (2 linear + ReLU) → residual (add the input back) |
| **Final output** | linear + softmax → a distribution over the vocabulary |

## Decoding (03 + Hugging Face "How to generate")

| Concept | Meaning |
|---|---|
| **Auto-regressive** | generate t₁, append, generate t₂, … until **[EOS]**; the length isn't fixed |
| **Greedy** | the highest-probability token each step; not the most probable sequence; repetitive |
| **Beam search** (`num_beams`) | keep the most likely sequences; good for predictable length (translation, summarization) |
| **n-gram penalty** (`no_repeat_ngram_size`) | no n-gram twice; careful ("New York") |
| **Sampling** (`do_sample`) | random according to probability; non-deterministic, may be incoherent |
| **Temperature** | low → sharper distribution; → 0 = greedy |
| **Top-k** (`top_k`) | sample among the k most likely; fixed k, doesn't adapt |
| **Top-p / nucleus** (`top_p`) | the smallest set with cumulative probability > p; adapts |
| **API parameters** | usually top-p and temperature |
| **HF conclusion** | top-p/top-k are more fluent for open-ended text; repetition comes from the model's training; no one-size-fits-all |
| **Degeneration** (Holtzman) | likelihood decoding → bland, repetitive; nucleus cuts the unreliable tail |
| **Beam search & UID** (Meister) | beam works by enforcing uniform information density |
| **Non-termination** (Choi) | decoding can repeat, never stop, or stop too early |
| **Unlikelihood** (Welleck) | the training objective is at fault; lower the probability of repeats |
| **η-sampling** (Hewitt) | truncation = desmoothing; an entropy-dependent threshold |
| **Speculative decoding** | a fast draft model + parallel verification: 2–3× faster, identical output; used in production |

## Lab 4: git (provisional)

| Concept | Meaning |
|---|---|
| **Content-addressed** | objects are named by the hash of their content; immutable |
| **Blob / tree / commit** | file content / directory / tree + parents + message |
| **`hash-object` / `cat-file`** | content → blob / read an object |
| **`write-tree` / `commit-tree`** | index → tree / tree → commit |
| **Ref / HEAD** | a mutable pointer (branch) / the current position; detached = points at a commit |
| **Reflog** | the history of HEAD; `git reset --hard <hash>` recovers lost commits |
