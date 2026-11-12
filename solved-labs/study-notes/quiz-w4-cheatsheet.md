# Quiz W4 cheat sheet

**Tokenization**
- LLMs see **tokens** (text pieces → IDs → vectors), not words.
- Goal: the **fewest tokens** for a vocabulary of at most **V**; input beyond the context length
  **L** is cut.
- **Sub-words** handle unknown words. **BPE** = repeatedly merge the most frequent pair
  (`e`+`s` → `es`).

**Language models**
- An LM computes **p(next token | previous tokens)**, which makes it a generative model.
- Trained with **cross-entropy**; evaluated with **perplexity** (lower = better).
- Bengio 2000: learn **word vectors** with the prediction (**representation learning**). This
  beats n-grams.

**Transformer**
- **Self-attention:** each token = a weighted mix of all tokens. **softmax(QKᵀ/√d)·V**.
- **Positional embeddings** add word order (RoPE is the most common).
- A block: attention → normalization → feed-forward → **residual**.

**Decoding**
- **Autoregressive:** predict → append → repeat until **[EOS]**.
- **Greedy:** best token each step, but not the best sequence. **Beam:** keep the b best
  sequences.
- **Temperature:** low = precise, high = creative.
- **Top-k:** among the k best tokens. **Top-p:** among the tokens that sum to probability p.
- Most-likely decoding gives **bland, repetitive** text, so use **top-p** sampling.
- **Speculative decoding:** a small model drafts, the big model checks. Faster, same output.
- Sampling → **different answers each time** → validate outputs and keep decisions deterministic.

**Lab 4: git** (provisional)
- Objects are named by the **hash of their content**: **blob** (file), **tree** (folder),
  **commit** (tree + parents + message).
- A **branch** is a pointer to a commit. **HEAD** is where you are now. **Detached HEAD** points
  straight to a commit.
- Lost commits → **`git reflog`** → `git reset --hard <hash>`.
