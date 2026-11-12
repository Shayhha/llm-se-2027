# Quiz W4 prep

**Scope:** the W3 lecture: `LLMs/` 01 (tokenization), 02 (next-token prediction), 02.5
(Transformers), 03 (decoding), ending with the Hugging Face post *How to generate text*
(von Platen). Plus lab 4 (git), provisional until the lab is published.

**The big picture: text in, text out.**

```
text ──encode──► token IDs ──model──► p(next token) ──decoding strategy──► next token ID
 ▲                                                                              │
 └──────────────decode◄────── append to the input and repeat until EOS ◄────────┘
```

---

## 1. Tokenization: encoding and decoding text

**What a tokenizer is:** a fixed, deterministic function between text and integers.

| | Input | Output |
|---|---|---|
| **Encode** (tokenize) | a string: `"Tokenization is fun"` | a list of integer **token IDs**, e.g. `[3404, 2065, 374, 2523]` (illustrative; the real IDs depend on the tokenizer) |
| **Decode** (detokenize) | a list of token IDs | the original string |

- **Reversible:** `decode(encode(text)) == text`, and the same text always gives the same IDs.
- Each ID is then looked up in the model's **embedding table** to get a vector. The model only
  ever sees IDs and vectors, never characters.

**Its purpose (why tokenize):**
1. **Numbers:** a neural network needs numbers, so text becomes IDs, then vectors.
2. **A fixed vocabulary of manageable size:** not one entry per possible word.
3. **No unknown words:** a rare or new word is split into known pieces, never `<UNK>`.

**Key parameters:**
- **Vocabulary size V:** how many distinct tokens exist (about 30k–100k+). A bigger vocabulary
  means fewer tokens per text, but a bigger model.
- **Context length L:** the maximum number of tokens the model handles at once (e.g. 4096).
  Longer input is **truncated**.

**The goal of a good tokenizer:** represent text with the **fewest tokens possible** for a
vocabulary of at most V. Fewer tokens means faster and cheaper, with more text fitting in the
context.

**Sub-word tokens**, between characters and whole words:
- inflections share a root: "learn" + "ing", "learn" + "ed";
- compounds split: "micro" + "processor";
- unseen words still work: "Kuber" + "net" + "es".

**BPE (byte pair encoding)** learns the vocabulary from a corpus:
1. start with every single character;
2. find the **most frequent adjacent pair** and merge it into one new token;
3. repeat until the vocabulary has V tokens.

Example: words `n e w e s t`, `w i d e s t` → merge `e`+`s` → `es` → merge `es`+`t` → `est`.
Text is first split at spaces with regular expressions, and BPE works inside each piece.

**Why it matters to us:** limits and cost are counted in **tokens**, not words. Code, rare words
and non-English text take more tokens.

### Remember it simply: tokenizer concepts

| Concept | Easy way to remember it |
|---|---|
| **Tokenizer** | a **dictionary-based translator** between text and numbers |
| **Encode** | **text → numbers.** "Write the sentence as dictionary page numbers." |
| **Decode** | **numbers → text.** "Look the page numbers up again." Always gives back the same text. |
| **Token** | a **Lego brick of text**: a word, part of a word, or a symbol |
| **Token ID** | the **brick's catalogue number** |
| **Vocabulary (V)** | the **box of all the bricks** the model owns |
| **Context length (L)** | **how many bricks fit on the table** at once; the rest falls off (truncated) |
| **Embedding** | the **meaning card** looked up for each catalogue number |
| **Sub-word** | **unknown word? Build it from smaller bricks** ("Kuber" + "net" + "es") |
| **BPE** | **glue the two bricks you see together most often into a new brick; repeat** |
| **Fewest tokens** | **fewer bricks = cheaper, faster, more text fits** |

---

## 2. The language model: next-token prediction

- **What it computes:** given the previous tokens, a **probability for every token in the
  vocabulary** being next: **p(tₙ | t₀ … tₙ₋₁)**. The last step is a **softmax**, which turns V
  scores into probabilities that sum to 1.
- Multiplying these step by step gives the probability of a whole text, so it's a **generative
  model**.
- **Training:** make the real next token as likely as possible (**cross-entropy loss**).
  **Evaluation:** **perplexity** (lower = better).
- **Main idea (Bengio 2000):** learn a **vector for each word** along with the prediction. Similar
  words get similar vectors, so the model handles sentences it never saw. This is
  **representation learning**, and it beat the old **n-gram** counting models.

## 3. The Transformer (the model inside)

- **Self-attention:** each token's vector is updated as a **weighted mix of all the tokens in the
  context**, with weights the model learns. **softmax(Q·Kᵀ/√d)·V**.
- **Positional embeddings** add word order, because attention alone ignores it (RoPE is most
  common).
- **GPT:** token embeddings + position → n Transformer blocks → softmax over the vocabulary.

---

## 4. Decoding: how text is generated (the Hugging Face post)

**Autoregressive generation:** the model gives only the *next-token* distribution. To write
text: choose a token, **append it to the input**, predict again. The length isn't fixed: it
stops when the model produces the **EOS** (end-of-sequence) token, or at a maximum length. The
**decoding strategy** is how we *choose* the token from the distribution.

| Method | How it chooses | Parameters (HF `generate`) | Pros | Cons |
|---|---|---|---|---|
| **Greedy search** | always the single most likely token | (default) | simple, fast, deterministic | misses a likely word hidden behind a less likely one; **repeats itself** |
| **Beam search** | keeps the `num_beams` most likely sequences, returns the best | `num_beams`, `early_stopping` | always at least as likely as greedy (not guaranteed best) | still **repetitive**; bland |
| **n-gram penalty** | forbids any n-gram appearing twice (probability set to 0) | `no_repeat_ngram_size` | removes repetition | blunt: "New York" could appear only once |
| **Sampling** | picks the next token **randomly by its probability** | `do_sample=True` | varied, not repetitive | often **incoherent**; non-deterministic |
| **Temperature** | reshapes the distribution: **low = sharper** (favours likely tokens), **high = flatter** | `temperature` | low → more coherent | → 0 behaves like greedy |
| **Top-k** (Fan et al. 2018) | samples only among the **k most likely** tokens | `top_k` (e.g. 50) | removes nonsense tokens; used by GPT-2 | k is **fixed**: too many choices when the model is sure, too few when it isn't |
| **Top-p / nucleus** (Holtzman et al. 2019) | samples from the **smallest set whose probabilities add up to p** | `top_p` (e.g. 0.92) | the set **adapts**: small when the model is sure, large when it isn't | — |
| **Top-k + top-p** | both filters together | `top_k=50, top_p=0.95` | common practical setting | — |

Also: `num_return_sequences` returns several outputs (beams or samples) to choose from.

### Remember it simply: decoding strategies

Picture the model offering a **menu of next words, each with a probability**:

| Strategy | Easy way to remember it |
|---|---|
| **Greedy** | **always order the top dish.** Safe, but you eat the same thing forever (repetition). |
| **Beam search** | **plan several meals ahead** and pick the best full plan. Great when the length is known (translation), boring for stories. |
| **n-gram penalty** | **"never the same 2 words twice"**: kills repeats, but also "New York" the second time. |
| **Sampling** | **roll a weighted die** over the whole menu. Varied, but can pick nonsense. |
| **Temperature** | **a thermostat for creativity**: cold (low) = sticks to favourites, hot (high) = wild picks, 0 = greedy. |
| **Top-k** | **roll the die only on the k best dishes.** Always the same number of choices, sure or not. |
| **Top-p (nucleus)** | **roll only on the dishes that together cover p%** (e.g. 92%). Few choices when the model is sure, many when unsure. **It adapts.** |
| **Top-k + top-p** | **both filters**: drop the junk, then adapt |
| **Conclusion** | **top-k/top-p for creative, open-ended text; beam for fixed-length tasks; no single winner** |

**Key arguments of the post:**
- **Beam search is good when the output length is predictable** (translation, summarization), but
  weak for **open-ended generation** (stories, dialogue).
- **Humans don't write the most probable words.** Good human text is *surprising* (Holtzman), so
  maximizing probability gives dull, repetitive text, called **degeneration**.

**The conclusion (where the lecture ended):**
1. For open-ended generation, **top-k and top-p sampling produce more fluent text** than greedy
   or beam search.
2. The repetition problem is **caused mostly by the model and how it was trained**, not only by
   the decoding method (Welleck et al.). Top-k and top-p can also repeat, and with a better
   training objective, beam search can win again.
3. **There is no one-size-fits-all method.** Choose the decoding strategy for the use case.

**Speculative decoding** (from file 03): a small model drafts tokens and the big model checks
them in parallel. It's faster with the same output, and it's used in production.

**Why it matters for software engineering:** with sampling, **the same prompt gives different
outputs**. So we validate every output and keep decisions in deterministic code, and for
repeatable runs we use temperature 0 (greedy) or caching.

---

## 5. Lab 4: git internals (provisional)

- Git stores **objects named by the hash of their content** (content-addressed, immutable):
  - **blob** = a file's content
  - **tree** = a directory
  - **commit** = a tree + parent commit(s) + message
- **The lab's commands:**
  - `hash-object`: file → blob
  - `cat-file`: read an object
  - `write-tree`: staging area → tree
  - `commit-tree`: tree → commit
- **Branch** = a movable pointer to a commit. **HEAD** = the current position. **Detached HEAD** =
  pointing straight at a commit.
- **Lost commits** (bad rebase or reset): `git reflog` shows where HEAD has been, then
  `git reset --hard <hash>`.

---

## Concepts to memorize

| Concept | Meaning |
|---|---|
| **Token** | a piece of text with an integer ID |
| **Tokenizer** | the deterministic, reversible function between text and token IDs |
| **Encode / decode** | text → token IDs / token IDs → text |
| **Token ID** | the integer for a token; it indexes the embedding table |
| **Embedding** | the vector the model uses for a token |
| **Vocabulary size V** | the number of distinct tokens |
| **Context length L** | the maximum tokens per input; extra is truncated |
| **Sub-word** | a word piece; handles rare and new words |
| **BPE** | builds the vocabulary by repeatedly merging the most frequent adjacent pair |
| **Language model** | gives p(next token \| previous tokens) |
| **Softmax** | turns scores into probabilities that sum to 1 |
| **Cross-entropy / perplexity** | training loss / evaluation score (lower = better) |
| **Representation learning** | learning vectors that capture meaning (Bengio) |
| **Self-attention** | each token = a learned weighted mix of all tokens |
| **Autoregressive** | generate one token at a time, feeding it back in |
| **EOS** | the end-of-sequence token; generation stops there |
| **Decoding strategy** | how the next token is chosen from the distribution |
| **Greedy** | always the most likely token |
| **Beam search** | keep the `num_beams` best sequences |
| **n-gram penalty** | forbid repeating any n-gram (`no_repeat_ngram_size`) |
| **Sampling** | choose randomly by probability (`do_sample=True`) |
| **Temperature** | low = sharper / safer, high = flatter / more creative |
| **Top-k** | sample among the k most likely tokens (fixed size) |
| **Top-p (nucleus)** | sample among the tokens covering probability p (adaptive) |
| **Degeneration** | dull, repetitive text from maximizing probability |
| **Open-ended generation** | stories and dialogue, where the length and content vary |
| **Speculative decoding** | a small model drafts, the big one verifies: faster, same output |
| **Blob / tree / commit** | git objects: file / directory / snapshot |
| **Reflog** | a log of where HEAD has been; recovers lost commits |

---

## Practice Q&A

**1.** What are the input and output of a tokenizer?
<details><summary>Answer</summary>Encode: input a string, output a list of integer token IDs. Decode: input token IDs, output the string. decode(encode(text)) = text.</details>

**2.** What is the purpose of tokenization?
<details><summary>Answer</summary>Turn text into numbers the network can use, keep a fixed vocabulary of manageable size, and handle any word (rare or new words are split into known pieces).</details>

**3.** What happens to a token ID inside the model?
<details><summary>Answer</summary>It is looked up in the embedding table and becomes a vector, which the Transformer processes.</details>

**4.** What do V and L mean, and what is the trade-off of a bigger V?
<details><summary>Answer</summary>V is the vocabulary size and L the maximum context length (longer input is truncated). A bigger V gives fewer tokens per text but a bigger model.</details>

**5.** Why sub-words rather than whole words or characters?
<details><summary>Answer</summary>Whole words need a huge vocabulary and fail on new words; characters make sequences very long. Sub-words keep the vocabulary fixed, share roots, and split unseen words into known pieces.</details>

**6.** Run BPE one step on `n e w e s t`, `w i d e s t`.
<details><summary>Answer</summary>The most frequent pair is `e`+`s`, so merge it into `es`: `n e w es t`, `w i d es t`. Next, `es`+`t` → `est`.</details>

**7.** What does a language model output at each step?
<details><summary>Answer</summary>A probability for every token in the vocabulary being next (a softmax over V tokens).</details>

**8.** What is autoregressive generation, and when does it stop?
<details><summary>Answer</summary>Choose a token, append it to the input, predict again; it stops at the EOS token or a maximum length.</details>

**9.** Greedy vs beam search?
<details><summary>Answer</summary>Greedy takes the most likely token each step and can miss better sequences. Beam search keeps the `num_beams` best sequences, so it finds sequences at least as likely, but both tend to repeat.</details>

**10.** What does `no_repeat_ngram_size` do, and what is its risk?
<details><summary>Answer</summary>It forbids any n-gram from appearing twice. The risk is that a phrase that legitimately repeats (e.g. "New York") can appear only once.</details>

**11.** What does temperature do? What happens as it approaches 0?
<details><summary>Answer</summary>It reshapes the distribution: low is sharper (likely tokens favoured, more coherent), high is flatter (more random). Near 0 it becomes greedy.</details>

**12.** Top-k vs top-p: which adapts, and why does that matter?
<details><summary>Answer</summary>Top-k always keeps k tokens. Top-p keeps the smallest set covering probability p, so it is small when the model is confident and large when it is unsure. Top-p adapts and avoids top-k's too-many or too-few choices.</details>

**13.** Why is beam search a poor choice for open-ended generation?
<details><summary>Answer</summary>It works when output length is predictable (translation, summarization); for stories and dialogue it gives dull, repetitive text, and humans don't write only the most probable words.</details>

**14.** What did the "How to generate" post conclude?
<details><summary>Answer</summary>Top-k and top-p give more fluent open-ended text than greedy or beam; repetition is mostly caused by how the model was trained; and there is no one-size-fits-all decoding method.</details>

**15.** Why can the same prompt give different answers, and what do we do about it?
<details><summary>Answer</summary>Sampling (temperature, top-k, top-p) picks randomly. We validate outputs and keep decisions deterministic; we use temperature 0 or caching for repeatable runs.</details>

**16.** (Lab 4) Name git's three object types, and how to recover lost commits.
<details><summary>Answer</summary>Blob (file), tree (directory), commit (tree + parents + message), all named by content hash. Recover lost commits with `git reflog` → `git reset --hard <hash>`.</details>
