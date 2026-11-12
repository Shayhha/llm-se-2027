# Quiz prep: week 4 quiz

**Scope:**
- **The W3 lecture:** `LLMs/` files 01 (tokenization), 02 (next-token prediction), 02.5
  (Transformers) and 03 (decoding strategies), the material covered in class.
- **This week's lab (lab 4):** git internals. Part E is based on the syllabus description, because
  the lab has not been published yet. It will be updated when it is.

Format: 5–10 minutes, short conceptual questions. Practice questions are at the end, with
answers.

---

# Part A: tokenization (`01 Tokenization in LLMs`)

## A1. What a token is, and why we tokenize
An LLM never sees characters or words, only **tokens**: pieces of text mapped to **integer
IDs**. Tokenization serves three purposes:
1. **Numerical conversion:** IDs are mapped to **embedding vectors** the network can compute on.
2. **Vocabulary management:** a vocabulary with one entry per word would need hundreds of
   thousands of entries, more across languages. Sub-word tokens keep it manageable.
3. **Unknown (out-of-vocabulary) words:** a new or rare word is split into known pieces instead
   of being replaced by `<UNK>`.

## A2. Tokenizer parameters
| Parameter | Meaning | Typical value |
|---|---|---|
| **Vocabulary size V** | how many distinct tokens exist | 30,000 to 100,000+ |
| **Max context length L** | how many tokens the model processes at once; longer input is **truncated** | 4096, 8192, more |

The trade-off for V: a larger vocabulary represents common words in one token, but makes the
model bigger and harder to train.

## A3. What a good tokenizer optimises
**Use the fewest tokens to represent the text, with a vocabulary no bigger than V.**

`minimize Σᵢ Tokens(Sentenceᵢ)` subject to `|Vocabulary| ≤ V`

Fewer tokens means faster and cheaper inference, and more text fits in the context window.

It must also be **deterministic and invertible**:
- `Detokenize(Tokenize(s)) == s`
- `Tokenize(Detokenize(tokens)) == tokens`

## A4. Why sub-words (not whole words, not single characters)
- **Inflections:** "learning", "learns", "learned" share the piece "learn", so their meaning stays
  related.
- **Compounds:** "microprocessor" → "micro" + "processor".
- **Unseen words:** "Kubernetes" → "Kuber" + "net" + "es", processed instead of becoming `<UNK>`.

## A5. Byte Pair Encoding (BPE), the main algorithm (used by GPT-3)
BPE is a **compression algorithm** that learns the vocabulary from a corpus:
1. **Start:** the vocabulary is every single character in the corpus.
2. **Merge:** find the **most frequent adjacent pair** and replace every occurrence with a new
   token.
3. **Repeat** until the vocabulary reaches size V, or no frequent pairs remain.

**Worked example.** Corpus: `l o w e r` ×5, `n e w e s t` ×2, `w i d e s t` ×3.
- Merge `e`+`s` → `es`: `n e w es t`, `w i d es t`.
- Merge `es`+`t` → `est`: `n e w est`, `w i d est`.
- Each merge adds one token to the vocabulary.
- A new word is tokenized with the learned pieces: `lowering` → `l o w er i n g` (if `er` was
  learned).

In practice the text is first split with regular expressions (at spaces) into chunks, and BPE
runs inside each chunk.

Tools to try it: Tiktokenizer (see how GPT models split text) and the Hugging Face tokenizer
playground. Deep dive: Karpathy's "Let's build the GPT tokenizer".

**Why it matters to a software engineer:**
- Cost, latency and context limits are counted in **tokens**, not words.
- Code, rare words and non-English text often take **more tokens**.

---

# Part B: next-token prediction (`02 LLM Next Token Prediction`)

## B1. A language model is a probability function
`LM: [t₀, …, tₙ₋₁] → p(tₙ | t₀ … tₙ₋₁)`

Given the previous tokens, it outputs a **probability distribution over the next token**.
- **The chain rule** turns this into a distribution over whole sequences:
  `p(t₀, …, tₙ) = p(t₀) · p(t₁ | t₀) · p(t₂ | t₀, t₁) · …`
- That is why an LM is a **generative model**: it models a distribution over complex events
  (all possible texts).

## B2. Training objective and evaluation
- **Objective:** maximize the log-likelihood of each real next token given the previous **k**
  tokens (the context window):
  `L₁(U) = Σᵢ log p(uᵢ | uᵢ₋ₖ, …, uᵢ₋₁; θ)`
- This is the **cross-entropy loss**. A good model gives **high probability to the token that
  actually appears**.
- **Evaluation:** **perplexity** on a test corpus, which measures how uncertain the model is about
  the real next tokens. **Lower is better.**

## B3. History: from n-grams to neural LMs
- **n-gram models** (1970s–2000s): count short word sequences. They generalize poorly, because
  most long sequences are never seen (the **curse of dimensionality**).
- **Neural probabilistic LM (Bengio et al., 2000):** learn at the same time
  1. a **distributed representation** (vector) for each word, and
  2. the probability function over sequences, expressed in those vectors.
- **Why it generalizes:** an unseen sentence gets high probability if its words are *similar*
  (close vectors) to words in seen sentences. Each training sentence informs the model about an
  exponential number of similar sentences.
- **Key concept: representation learning** (latent representations), the idea behind LLMs'
  success.
- LMs are **better than humans at next-token prediction**, even small ones like GPT-3 Ada
  (Shlegeris et al., 2024, measured by top-1 accuracy and perplexity).

## B4. The GPT formula (decoder-only Transformer, Radford et al. 2018)
1. **Input embedding:** `h₀ = U·Wₑ + Wₚ` (token embeddings + **position** embeddings).
2. **n layers:** `hₗ = transformer_block(hₗ₋₁)`.
3. **Output:** `p(u) = softmax(hₙ·Wₑᵀ)`, a vector of **V** probabilities (one per token
   in the vocabulary, summing to 1).

Everything (Wₑ, Wₚ, the blocks) is trained **end to end** on the LM objective.

---

# Part C: the Transformer (`02.5 Transformers`)

- **Origin:** "Attention Is All You Need" (Vaswani et al., NeurIPS 2017). It replaced RNNs,
  LSTMs and GRUs.
- **Positional embeddings:** self-attention by itself ignores word order, so position information
  is added. The three kinds:
  - **sinusoidal** (fixed sine and cosine functions);
  - **learned** (trained);
  - **RoPE** (2021), the most common today.
- **Self-attention:** each token's new representation is a **weighted combination of the other
  tokens' representations**. The model learns how to compute the weights (how much each token
  influences each other).
  - `Q = X·W_Q`, `K = X·W_K`, `V = X·W_V` (query, key, value)
  - `Attention(Q, K, V) = softmax(Q·Kᵀ / √d_k) · V`
  - **Multi-head:** several attentions in parallel, each learning different relationships.
- **One transformer block, in order:**
  1. multi-head self-attention;
  2. **layer normalization** (zero mean, unit variance);
  3. **feed-forward network**: `ReLU(X·W₁ + b₁)·W₂ + b₂`;
  4. **residual connection**: add the block's input back, preserving information.
- **End:** a final linear layer + softmax gives the distribution over the vocabulary.

---

# Part D: decoding strategies (`03 LM Decoding Strategies and Parameters`)

## D1. Autoregressive generation
To generate text: predict the next token, **append it to the prompt**, predict again, until the
special **[EOS]** (end-of-sequence) token.

## D2. The strategies
| Strategy | How it picks the next token | Property |
|---|---|---|
| **Greedy** | always the single most likely token | fast, deterministic; **not** the most likely *sequence* (a likely first token can hide better paths) |
| **Beam search** | keeps the **b best partial sequences** at each step | finds higher-probability sequences; can still be bland |
| **Temperature** | divides the scores before softmax: low → sharper, high → flatter | low = precise, repetitive; high = diverse, random |
| **Top-k** | samples only among the **k** most likely tokens | cuts the unlikely tail; k is fixed regardless of the distribution |
| **Top-p (nucleus)** | samples from the **smallest set whose probabilities sum to p** | the set grows or shrinks with the model's certainty |

APIs usually expose **temperature** and **top-p** (e.g. OpenAI's chat completion parameters).

## D3. What the research papers say (one line each)
- **Neural text degeneration (Holtzman et al., 2020):** using likelihood as the *decoding*
  objective makes **bland, strangely repetitive** text, unlike human text. **Nucleus sampling**
  keeps diversity while cutting the unreliable **tail**.
- **"If beam search is the answer…" (Meister et al., 2020):** exact most-likely decoding (MAP)
  often gives poor text. Beam search works because it favours **uniform information density**.
  High probability alone ≠ good text.
- **Non-terminating sequences (Choi et al., 2022):** greedy, beam, top-k and nucleus can produce
  **repetition, never-ending or too-early-ending** text. They propose a self-terminating LM.
- **Unlikelihood training (Welleck et al., ICLR 2020):** the *training* objective is also at
  fault: it gives too much probability to repeats and frequent words. Teach the model to give
  them **low** probability.
- **η-sampling (Hewitt et al., EMNLP 2022):** truncation (top-k, top-p) is "desmoothing". Top-p
  can cut good words, so η-sampling uses a threshold that depends on the **entropy**.

## D4. Speculative decoding (Leviathan et al., ICML 2023)
- Decoding K tokens needs K **sequential** runs of the big model, which is slow.
- A **small, cheap model drafts** several tokens. The big model **checks them in parallel** and
  keeps the correct ones.
- 2–3× faster, with **identical outputs**. It is the method most used in production today.

## D5. Why decoding matters for software engineering
The **same model and prompt can give different outputs** depending on decoding (temperature,
top-p). That is why LLM output is non-deterministic, why we **validate** it (W1, W3), and why
we ran reproducible experiments with caching.

---

# Part E: lab 4: git internals (provisional, from the syllabus)

> The lab has not been published yet. The syllabus says: *"Implement a miniature git in ~100
> lines (`hash-object`, `cat-file`, `write-tree`, `commit-tree`), deliberate disaster-recovery
> exercise (detached HEAD, lost commits, botched rebase, recovery via reflog)."* This section will
> be updated when the lab is out.

## E1. Git is a content-addressed object store
Every piece of data is an **object**, named by the **hash of its content** (SHA-1, 40 hex
characters). The same content always gets the same name, and changing the content changes the
name.

| Object | Stores | Points to |
|---|---|---|
| **blob** | one file's content (no name) | nothing |
| **tree** | a directory: names + modes → blob or tree hashes | blobs and trees |
| **commit** | a snapshot: one tree, parent commit(s), author, message | its tree and parent(s) |

- **How an object is stored:** header `"<type> <size>\0"` + content → hash it → compress (zlib)
  → save at `.git/objects/ab/cdef…` (the first 2 characters form the folder name).
- Objects are **immutable**. History is a **DAG** (a directed acyclic graph) of commits.

## E2. The four plumbing commands the lab implements
| Command | Does |
|---|---|
| `hash-object` | hashes a file as a blob (with `-w`, also writes it to `.git/objects`) |
| `cat-file` | reads an object back: its type, size or content |
| `write-tree` | turns the staging area (index) into a tree object |
| `commit-tree` | makes a commit object from a tree (+ parent + message) |

High-level commands (`add`, `commit`) are built on these.

## E3. Refs, HEAD and the three trees
- **A ref** (branch, tag) is a **mutable pointer**: a file containing a commit hash
  (`.git/refs/heads/main`).
- **HEAD** points to the current branch (`ref: refs/heads/main`). In **detached HEAD**, it points
  straight to a commit.
- **The three trees:**
  - **HEAD** (the last commit);
  - **the index** (the staging area: what the next commit will contain);
  - **the working directory** (your files).
- **Remotes** are just other repositories.

## E4. Disaster recovery
- **The reflog** records **every position HEAD and the branches have had**, including "lost"
  commits. `git reflog` → find the hash → `git reset --hard <hash>` or `git branch rescue <hash>`.
- **Detached HEAD:** commits made there belong to no branch. Save them with `git branch <name>`
  (or `git switch -c`) before switching away, or recover them from the reflog.
- **Botched rebase:** rebase **creates new commits**; the old ones still exist. Undo with the
  reflog, or with `ORIG_HEAD`.
- **Derived concepts:** stash, rebase, reset, cherry-pick and reflog are all built from objects +
  refs. Nothing is truly lost until garbage collection.

## E5. Link to the W4 lecture theme (domain models)
Git is the course's example of a strong **domain model**: a few concepts (blob, tree, commit,
ref) explain everything. Git is also a **ubiquitous-language counterexample**: its *commands*
use confusing names for its clean concepts. `checkout` does several unrelated things, and
`reset` has three modes.

---

# Practice questions

**1.** Give three reasons LLMs use tokenization.
<details><summary>Answer</summary>Convert text to integer IDs mapped to vectors; keep the vocabulary a manageable size; handle unknown or rare words by splitting them into known sub-words instead of `<UNK>`.</details>

**2.** What are a tokenizer's vocabulary size V and max context length L? What happens past L?
<details><summary>Answer</summary>V = the number of distinct tokens (≈30k–100k+). L = the maximum number of tokens processed at once (e.g. 4096). Input longer than L is truncated.</details>

**3.** What does a good tokenizer optimise, and why does it matter?
<details><summary>Answer</summary>The fewest tokens to represent the text, given a vocabulary of at most V. Shorter sequences are faster and cheaper, and more text fits in the context window.</details>

**4.** What two properties must a tokenizer have?
<details><summary>Answer</summary>Deterministic and invertible: `Detokenize(Tokenize(s)) == s` and `Tokenize(Detokenize(tokens)) == tokens`.</details>

**5.** Why sub-word tokens instead of whole words?
<details><summary>Answer</summary>Shared roots for inflections (learn-ing/-ed), splitting compounds (micro+processor), and handling unseen words (Kuber+net+es), all with a fixed-size vocabulary.</details>

**6.** Describe BPE and apply one merge to `n e w e s t`, `w i d e s t`.
<details><summary>Answer</summary>Start from single characters; repeatedly merge the most frequent adjacent pair into a new token until the vocabulary reaches V. The most frequent pair is `e`+`s` → `es`: `n e w es t`, `w i d es t` (and then `es`+`t` → `est`).</details>

**7.** What does a language model compute? Write it.
<details><summary>Answer</summary>A probability distribution over the next token given the previous ones: p(tₙ | t₀…tₙ₋₁). By the chain rule this also defines a distribution over whole sequences, so it is a generative model.</details>

**8.** What is the LM training objective, and how is an LM evaluated?
<details><summary>Answer</summary>Maximize the log-likelihood of each actual next token given the previous k tokens (cross-entropy loss). Evaluated with perplexity on a test corpus; lower is better.</details>

**9.** What was the key idea of Bengio et al.'s neural LM, and why does it generalize better than n-grams?
<details><summary>Answer</summary>Learn a distributed vector representation for each word together with the probability function (representation learning). An unseen sentence still gets high probability if its words are close to words in seen sentences, which beats the curse of dimensionality that limits n-grams.</details>

**10.** Write the three steps of the GPT model.
<details><summary>Answer</summary>h₀ = U·Wₑ + Wₚ (token + position embeddings); hₗ = transformer_block(hₗ₋₁) for n layers; p(u) = softmax(hₙ·Wₑᵀ), a distribution over V tokens.</details>

**11.** Why do Transformers need positional embeddings? Name three kinds.
<details><summary>Answer</summary>Self-attention ignores order, so without them "dog bites man" = "man bites dog". Sinusoidal, learned, RoPE (most common now).</details>

**12.** Explain self-attention and write its formula.
<details><summary>Answer</summary>Each token's new representation is a learned weighted mix of all tokens' representations. Q=XW_Q, K=XW_K, V=XW_V; Attention = softmax(QKᵀ/√d_k)·V. Multi-head runs several in parallel.</details>

**13.** List the parts of one Transformer block in order.
<details><summary>Answer</summary>Multi-head self-attention → layer normalization → feed-forward network (two linear layers with a ReLU) → residual connection (add the input back).</details>

**14.** What is autoregressive generation, and when does it stop?
<details><summary>Answer</summary>Predict a token, append it to the context, predict the next, and so on, until the special [EOS] token (or a length limit).</details>

**15.** Greedy vs beam search: what is the weakness of greedy?
<details><summary>Answer</summary>Greedy takes the single most likely token each step, which doesn't guarantee the most likely sequence: a likely first token can hide better continuations. Beam search keeps the b best partial sequences.</details>

**16.** Temperature vs top-k vs top-p.
<details><summary>Answer</summary>Temperature sharpens (low) or flattens (high) the distribution: precise vs diverse. Top-k samples among the k most likely tokens (fixed size). Top-p (nucleus) samples from the smallest set whose probabilities sum to p, so it adapts to how certain the model is.</details>

**17.** What is "neural text degeneration", and what fixes it?
<details><summary>Answer</summary>Maximizing likelihood when decoding produces bland, repetitive text, unlike human text (Holtzman et al.). Nucleus (top-p) sampling keeps diversity while cutting the unreliable tail. Unlikelihood training fixes it at training time.</details>

**18.** What is speculative decoding?
<details><summary>Answer</summary>A small fast model drafts several tokens and the big model verifies them in parallel. It is 2–3× faster with identical outputs, and is used in production.</details>

**19.** Why does the same prompt give different outputs, and what do we do about it in software?
<details><summary>Answer</summary>Decoding samples from a distribution (temperature, top-p), so outputs vary. We validate every output against a schema, keep decisions in deterministic code, and use caching or temperature 0 for reproducibility.</details>

**20.** (Lab 4) What are git's three object types, and what does each point to?
<details><summary>Answer</summary>Blob (file content, points to nothing); tree (a directory: names → blob or tree hashes); commit (a tree + parent commits + author and message). All are named by the hash of their content.</details>

**21.** (Lab 4) What does "content-addressed" mean, and why are objects immutable?
<details><summary>Answer</summary>An object's name is the hash of its content, so the same content gives the same name. Changing content would change the hash, so you create a new object instead of modifying the old one.</details>

**22.** (Lab 4) What are refs and HEAD? What is a detached HEAD?
<details><summary>Answer</summary>A ref is a mutable pointer (a file holding a commit hash, e.g. a branch). HEAD points to the current branch. Detached HEAD = HEAD points directly to a commit, so new commits there belong to no branch.</details>

**23.** (Lab 4) You ran a bad rebase and your commits "disappeared". How do you get them back?
<details><summary>Answer</summary>The old commits still exist. Run `git reflog`, find the hash from before the rebase, and `git reset --hard <hash>` (or create a branch there). `ORIG_HEAD` also points to the pre-rebase state.</details>
