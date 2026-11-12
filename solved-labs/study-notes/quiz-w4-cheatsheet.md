# Quiz W4 cheat sheet: the things to remember

Week-4 quiz: the W3 lecture (`LLMs/` 01, 02, 02.5, 03) + lab 4 (git internals, provisional).
Full notes: `quiz-w4-prep.md`.

## Tokenization

**1. LLMs see tokens, not words.** Tokens are text pieces mapped to **integer IDs**, then to
vectors. Why: numbers for the network, a **manageable vocabulary**, and **unknown words** split
into known pieces (no `<UNK>`).

**2. Parameters:** **vocabulary size V** (30k–100k+) and **max context length L** (e.g. 4096;
longer input is **truncated**).

**3. Goal:** the **fewest tokens** for a vocabulary of at most V, so it is faster, cheaper, and
more text fits. It must be **deterministic and invertible**: `Detokenize(Tokenize(s)) == s`.

**4. Sub-words:** inflections (learn-ing), compounds (micro+processor), unseen words
(Kuber+net+es).

**5. BPE:** start from characters → **merge the most frequent adjacent pair** → repeat until
size V. Example: `e`+`s` → `es`, then `es`+`t` → `est`.

## Next-token prediction

**6. A language model = p(next token | previous tokens).** By the chain rule it is a distribution
over whole texts, a **generative model**.

**7. Training:** maximize the log-likelihood of the real next token (**cross-entropy**).
**Evaluation:** **perplexity**, lower is better.

**8. Bengio 2000:** learn a **vector per word** + the probability function together. This is
**representation learning**: similar words get close vectors, so unseen sentences still get
sensible probabilities. It beats n-grams and the curse of dimensionality.

**9. GPT:** h₀ = token emb + **position** emb → **n transformer blocks** → **softmax** over V
tokens. LMs beat humans at next-token prediction.

## Transformers

**10. Self-attention:** each token = a **learned weighted mix of all tokens**.
**softmax(QKᵀ/√d_k)·V**, with Q, K, V = X times learned matrices. **Multi-head** = several
attentions in parallel.

**11. Positional embeddings** are needed because attention ignores order: **sinusoidal**,
**learned**, **RoPE** (most common).

**12. Block:** attention → **layer norm** → **feed-forward** (ReLU) → **residual** (add the input
back).

## Decoding

**13. Autoregressive:** predict → append → repeat until **[EOS]**.

**14. The strategies:**

| | Picks | Note |
|---|---|---|
| **Greedy** | the most likely token | not the most likely **sequence** |
| **Beam** | keeps the b best partial sequences | better sequences, can be bland |
| **Temperature** | low = sharp, high = flat | precise vs diverse |
| **Top-k** | among the k most likely | fixed size |
| **Top-p (nucleus)** | the smallest set with total probability p | adapts to certainty |

**15. Degeneration:** maximizing likelihood when decoding → **bland, repetitive** text. Fixes:
**nucleus sampling** (decoding) or **unlikelihood training** (training). Other failures:
never-ending or too-early-ending output.

**16. Speculative decoding:** a **small model drafts**, the **big model verifies in parallel** →
2–3× faster, **identical output**. Used in production.

**17. The link:** decoding samples, so **the same prompt gives different outputs**. That is why we
**validate** output and keep decisions **deterministic**.

## Lab 4: git internals (provisional)

**18. Content-addressed store:** every object is named by the **hash of its content**, and is
**immutable**.
- **blob** = file content
- **tree** = directory (names → hashes)
- **commit** = tree + parent(s) + message

History is a **DAG**.

**19. Plumbing:** `hash-object` (content → blob hash), `cat-file` (read an object), `write-tree`
(index → tree), `commit-tree` (tree → commit).

**20. Refs and HEAD:** a ref (branch) is a **mutable pointer** to a commit; HEAD points to the
current branch. **Detached HEAD** points straight to a commit. **Three trees:** HEAD, the index,
the working directory.

**21. Recovery:** **`git reflog`** lists every place HEAD has been → `git reset --hard <hash>` or
`git branch rescue <hash>`. Rebase makes **new** commits, and the old ones remain (`ORIG_HEAD`).

---

# Quick self-test

Cover the sheet and answer from memory. The answers are on the next page.

1. Three reasons to tokenize.
2. What are V and L, and what happens past L?
3. What does a good tokenizer minimise? Which two properties must it have?
4. Do one BPE merge on `w i d e s t` + `n e w e s t`.
5. Write what a language model computes.
6. What is the training objective, and how is an LM evaluated?
7. What was Bengio's key idea?
8. The attention formula, and why positional embeddings are needed.
9. The parts of a transformer block, in order.
10. Greedy vs beam search: what is greedy's weakness?
11. Temperature vs top-k vs top-p.
12. What is neural text degeneration, and two fixes?
13. What is speculative decoding?
14. Git's three object types.
15. A rebase lost your commits: how do you recover them?

# Self-test answers

1. Text → integer IDs → vectors; a manageable vocabulary; unknown words split into known pieces.
2. V = vocabulary size (30k–100k+); L = max tokens at once (e.g. 4096); longer input is truncated.
3. The total number of tokens (with |vocabulary| ≤ V). Deterministic + invertible.
4. The most frequent pair is `e`+`s` → `es`: `w i d es t`, `n e w es t`.
5. p(tₙ | t₀…tₙ₋₁): a distribution over the next token given the previous ones.
6. Maximize the log-likelihood of the real next token (cross-entropy); perplexity, lower is better.
7. Learn word vectors together with the probability function (representation learning), so
   similar words generalize.
8. softmax(QKᵀ/√d_k)·V. Attention ignores order, so position must be added (sinusoidal, learned,
   RoPE).
9. Multi-head attention → layer norm → feed-forward → residual connection.
10. Greedy takes the best token each step, which is not necessarily the best sequence. Beam keeps
    the b best sequences.
11. Temperature = sharp vs flat distribution; top-k = k most likely; top-p = the smallest set
    summing to p (adapts).
12. Likelihood-maximizing decoding gives bland, repetitive text. Fixes: nucleus sampling;
    unlikelihood training.
13. A small model drafts tokens and the big one verifies them in parallel: faster, with identical
    output.
14. Blob (file content), tree (directory), commit (tree + parents + message).
15. `git reflog` → find the old hash → `git reset --hard <hash>` (or `ORIG_HEAD`).
