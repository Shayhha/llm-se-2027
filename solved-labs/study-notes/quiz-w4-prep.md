# Quiz W4 prep

**Scope:** the W3 lecture, `LLMs/` files 01, 02, 02.5 and 03 (tokenization, next-token
prediction, Transformers, decoding), plus lab 4 (git internals). The lab part follows the
syllabus, because the lab isn't published yet.

---

## 1. Tokenization

- **LLMs work on tokens, not words.** A token is a piece of text with an integer ID, mapped to a
  vector.
- **Why tokenize:**
  - turn text into numbers;
  - keep the **vocabulary** a manageable size;
  - handle **unknown words** by splitting them into known pieces.
- **Two parameters:** **vocabulary size V** (30k–100k+) and **context length L** (the maximum
  number of tokens; longer input is **truncated**).
- **Goal:** the **fewest tokens** for a vocabulary of at most V, so it's cheaper and faster, and
  more text fits. It must be **reversible**: detokenize(tokenize(text)) = text.
- **Sub-words:** "learn-ing", "micro-processor", "Kuber-net-es". Related words share pieces, and
  nothing is unknown.
- **BPE (byte pair encoding):** start from single characters, then **repeatedly merge the most
  frequent adjacent pair** into a new token, until the vocabulary reaches V.
  Example: `e`+`s` → `es`, then `es`+`t` → `est`.

## 2. Next-token prediction

- **A language model computes p(next token | previous tokens)**, a probability over the whole
  vocabulary.
- Repeating it gives a probability for whole texts (chain rule), so it's a **generative model**.
- **Training:** make the real next token as likely as possible (**cross-entropy loss**).
- **Evaluation:** **perplexity**, how "surprised" the model is by real text. Lower is better.
- **Bengio et al. (2000):** instead of counting word sequences (**n-grams**), learn a **vector per
  word** together with the prediction. Similar words get similar vectors, so the model handles
  sentences it never saw. This is **representation learning**, the idea behind LLMs.
- **GPT in three steps:**
  1. token embedding + **position** embedding;
  2. **n transformer blocks**;
  3. **softmax** → a probability for each of the V tokens.
- LMs are **better than humans** at next-token prediction.

## 3. The Transformer

- **"Attention Is All You Need" (2017)** replaced RNNs and LSTMs.
- **Self-attention:** each token's representation becomes a **learned weighted mix of all the
  tokens**, so it can use any word in the context.
  **Attention = softmax(Q·Kᵀ / √d_k) · V** (queries, keys, values). **Multi-head** = several
  attentions in parallel.
- **Positional embeddings:** attention ignores word order, so position is added. The kinds are
  sinusoidal, learned, and **RoPE** (most common).
- **One block:** attention → layer normalization → feed-forward network → **residual connection**
  (add the input back).

## 4. Decoding (how text is generated)

- **Autoregressive:** pick a token, append it, predict again, until **[EOS]** (end of sequence).

| Strategy | What it does | Key point |
|---|---|---|
| **Greedy** | always the most likely token | not the best overall **sequence** |
| **Beam search** | keeps the b best sequences | better sequences, can be bland |
| **Temperature** | low = sharp, high = flat distribution | precise ↔ creative |
| **Top-k** | samples among the k most likely | fixed size |
| **Top-p (nucleus)** | samples from the smallest set with total probability p | adapts to the model's certainty |

- **Degeneration:** always choosing the most likely text gives **bland, repetitive** output.
  The fix is **nucleus sampling**, which cuts the unreliable tail but keeps variety.
- **Other failures:** repetition, never stopping, stopping too early.
- **Speculative decoding:** a **small model drafts** tokens and the **big model checks** them in
  parallel. It's 2–3× faster with the **same output**, and it's what production systems use.
- **Why it matters to us:** sampling means the **same prompt can give different answers**. So we
  **validate** outputs and keep decisions in **deterministic** code.

## 5. Lab 4: git internals (provisional)

- **Git is a content-addressed store:** every object is named by the **hash of its content**, and
  objects never change.
  - **blob** = a file's content
  - **tree** = a directory (names → hashes)
  - **commit** = a tree + parent commit(s) + a message
- **The four commands the lab implements:**
  - `hash-object`: file → blob
  - `cat-file`: read an object
  - `write-tree`: staging area → tree
  - `commit-tree`: tree → commit
- **Refs:** a branch is a movable pointer to a commit. **HEAD** points to the current branch.
  **Detached HEAD** points straight to a commit.
- **Recovery:** **`git reflog`** lists everywhere HEAD has been, so "lost" commits after a bad
  rebase or reset can be found and restored with `git reset --hard <hash>`.

---

## Concepts to memorize

| Concept | Meaning |
|---|---|
| **Token** | a piece of text with an integer ID; what the LLM actually processes |
| **Vocabulary size (V)** | the number of distinct tokens the model knows |
| **Context length (L)** | the maximum number of tokens processed at once; extra is cut |
| **Sub-word tokenization** | splitting words into frequent pieces; no unknown words |
| **BPE** | builds the vocabulary by repeatedly merging the most frequent pair |
| **Language model** | p(next token \| previous tokens) |
| **Generative model** | a model of a probability distribution over data (all possible texts) |
| **Cross-entropy** | the training loss: how unlikely the real next token was |
| **Perplexity** | the evaluation score: the model's uncertainty on real text (lower = better) |
| **n-gram model** | the old approach: counts short word sequences |
| **Representation learning** | learning vectors (embeddings) that capture meaning |
| **Embedding** | the vector for a token |
| **Positional embedding** | adds word order (sinusoidal / learned / RoPE) |
| **Self-attention** | each token = a weighted mix of all tokens; softmax(QKᵀ/√d)V |
| **Multi-head attention** | several attentions in parallel |
| **Residual connection** | adds a block's input back to its output |
| **Softmax** | turns scores into probabilities that sum to 1 |
| **Autoregressive** | generate one token at a time, feeding each back in |
| **[EOS]** | the end-of-sequence token that stops generation |
| **Greedy / beam search** | most likely token / keep the b best sequences |
| **Temperature** | how sharp or flat the sampling distribution is |
| **Top-k / top-p** | sample among k tokens / among tokens totalling probability p |
| **Degeneration** | bland, repetitive output from likelihood-maximizing decoding |
| **Speculative decoding** | a small model drafts, the big one verifies: faster, same output |
| **Blob / tree / commit** | git objects: file content / directory / snapshot + history |
| **Content-addressed** | named by the hash of the content |
| **Ref / HEAD** | a movable pointer to a commit / the current position |
| **Reflog** | the history of where HEAD has been; used to recover commits |

---

## Practice Q&A

**1.** Why do LLMs tokenize text?
<details><summary>Answer</summary>To turn text into numbers, keep the vocabulary small, and handle unknown words by splitting them into known pieces.</details>

**2.** What does a good tokenizer optimise?
<details><summary>Answer</summary>The fewest tokens for a fixed vocabulary size, which makes it cheaper and faster and fits more text in the context. It must also be reversible.</details>

**3.** How does BPE build its vocabulary?
<details><summary>Answer</summary>Start from characters and repeatedly merge the most frequent adjacent pair into a new token until the vocabulary reaches size V.</details>

**4.** What does a language model compute?
<details><summary>Answer</summary>A probability distribution over the next token given the previous tokens.</details>

**5.** How is a language model trained and evaluated?
<details><summary>Answer</summary>Trained to make the real next token likely (cross-entropy loss). Evaluated with perplexity; lower is better.</details>

**6.** Why did neural LMs beat n-gram models?
<details><summary>Answer</summary>They learn word vectors, so similar words behave similarly and unseen sentences still get sensible probabilities (representation learning).</details>

**7.** What does self-attention do?
<details><summary>Answer</summary>It updates each token's representation as a learned weighted mix of all tokens in the context: softmax(QKᵀ/√d)·V.</details>

**8.** Why are positional embeddings needed?
<details><summary>Answer</summary>Attention ignores word order; positional embeddings add it (sinusoidal, learned, RoPE).</details>

**9.** What is autoregressive generation?
<details><summary>Answer</summary>Generate one token, append it to the input, predict the next, and repeat until [EOS].</details>

**10.** What is the weakness of greedy decoding?
<details><summary>Answer</summary>Picking the best token at each step doesn't guarantee the best overall sequence.</details>

**11.** Temperature vs top-k vs top-p?
<details><summary>Answer</summary>Temperature makes the distribution sharper or flatter; top-k samples among the k most likely tokens; top-p samples from the smallest set whose probabilities sum to p.</details>

**12.** What is text degeneration, and what fixes it?
<details><summary>Answer</summary>Likelihood-maximizing decoding produces bland, repetitive text. Nucleus (top-p) sampling fixes it by cutting the unlikely tail while keeping variety.</details>

**13.** What is speculative decoding?
<details><summary>Answer</summary>A small model drafts tokens and the big model verifies them in parallel: faster, with identical output.</details>

**14.** Why can the same prompt give different outputs, and what do we do about it?
<details><summary>Answer</summary>Decoding samples from a distribution. We validate outputs and keep decisions in deterministic code.</details>

**15.** (Lab 4) Name git's three object types.
<details><summary>Answer</summary>Blob (file content), tree (directory), commit (tree + parents + message), each named by the hash of its content.</details>

**16.** (Lab 4) How do you recover commits lost in a bad rebase?
<details><summary>Answer</summary>Find the old commit hash in `git reflog`, then `git reset --hard <hash>` (or create a branch there).</details>
