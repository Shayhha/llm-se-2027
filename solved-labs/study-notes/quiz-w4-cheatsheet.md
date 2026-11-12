# Quiz W4 cheat sheet

**Text in, text out:** text → **encode** → token IDs → model → p(next token) → **decoding
strategy** → token → append → repeat until **EOS** → **decode** → text.

**Tokenizer**
- **Encode:** string → list of integer **token IDs**. **Decode:** IDs → string. It's
  deterministic and reversible.
- **Purpose:** numbers for the network, a fixed vocabulary, **no unknown words** (sub-words).
- Each ID is looked up as an **embedding** vector.
- **V** = vocabulary size (30k–100k+). **L** = context length (longer input is truncated).
  Goal: the **fewest tokens**.
- **BPE:** start from characters, repeatedly **merge the most frequent pair** (`e`+`s` → `es`)
  until the vocabulary has V tokens.

**Language model**
- Outputs **p(next token | previous tokens)** over the whole vocabulary (**softmax**).
- Training: cross-entropy. Evaluation: **perplexity** (lower = better).
- Learns **word vectors** (Bengio, representation learning). The Transformer uses
  **self-attention**: each token = a weighted mix of all tokens.

**Decoding (Hugging Face "How to generate")**
- **Greedy:** the most likely token. Simple, but **repetitive** and misses better sequences.
- **Beam search** (`num_beams`): keeps the best b sequences. Good for **translation and
  summaries**, dull for open-ended text.
- **n-gram penalty** (`no_repeat_ngram_size`): no repeated n-grams. Careful: "New York" only once.
- **Sampling** (`do_sample`): random by probability. Varied, but can be incoherent.
- **Temperature:** low = safe and sharp (→ 0 = greedy), high = creative.
- **Top-k:** among the k most likely tokens (fixed). **Top-p:** among the tokens covering
  probability p (**adapts**).
- **Conclusion:** top-k and top-p are more fluent for open-ended text; repetition comes mostly
  from **training**; **no one-size-fits-all**.
- Sampling means **different outputs for the same prompt**, so validate and keep decisions
  deterministic.

**Lab 4: git** (provisional)
- Objects are named by **content hash**: **blob** (file), **tree** (folder), **commit** (tree +
  parents + message).
- **Branch** = a pointer, **HEAD** = where you are. Lost commits → **`git reflog`** →
  `git reset --hard <hash>`.
