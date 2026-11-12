# Quiz W4 cheat sheet

**Text in, text out:** text → **encode** → token IDs → model → p(next token) → **decoding
strategy** → token → append → repeat until **EOS** → **decode** → text.

## Tokenizer

| Concept | Meaning |
|---|---|
| **Tokenizer** | a deterministic, reversible translator between text and numbers |
| **Encode** | string → list of integer **token IDs** |
| **Decode** | token IDs → the same string back |
| **Token / token ID** | a piece of text (word, sub-word, symbol) / its integer number |
| **Embedding** | the vector the model looks up for each ID |
| **Vocabulary size V** | how many distinct tokens exist (30k–100k+) |
| **Context length L** | the maximum tokens at once; extra is truncated |
| **Sub-word** | splits rare or new words into known pieces, so there are no unknown words |
| **BPE** | start from characters, repeatedly merge the most frequent pair (`e`+`s` → `es`) |
| **Goal** | the fewest tokens for a vocabulary of at most V: cheaper, faster, more fits |

## Language model

| Concept | Meaning |
|---|---|
| **Language model** | p(next token \| previous tokens) over the whole vocabulary |
| **Softmax** | turns scores into probabilities that sum to 1 |
| **Perplexity** | how "surprised" the model is by real text (lower = better) |
| **Representation learning** | learning word vectors with the prediction (Bengio); beats n-grams |
| **Self-attention** | each token = a learned weighted mix of all tokens |
| **Autoregressive / EOS** | generate one token at a time and feed it back / the stop token |

## Decoding (Hugging Face "How to generate")

| Strategy | Meaning |
|---|---|
| **Greedy** | always the most likely token. Simple, but repetitive. |
| **Beam search** (`num_beams`) | keep the best b sequences. Good for translation and summaries, dull for stories. |
| **n-gram penalty** (`no_repeat_ngram_size`) | no repeated n-grams (careful: "New York" only once) |
| **Sampling** (`do_sample`) | random by probability. Varied, may be incoherent. |
| **Temperature** | low = safe and sharp (0 = greedy), high = creative |
| **Top-k** | sample among the k most likely tokens (fixed number) |
| **Top-p / nucleus** | sample among the tokens covering probability p (**adapts**) |

**Conclusion:** top-k and top-p are more fluent for open-ended text; repetition comes mostly from
training; **no one-size-fits-all**. Sampling means **different outputs** for the same prompt, so
validate the output and keep decisions deterministic.

## Lab 4: git (provisional)

| Concept | Meaning |
|---|---|
| **Blob / tree / commit** | file content / directory / snapshot + parents + message |
| **Content-addressed** | each object is named by the hash of its content |
| **Branch / HEAD** | a movable pointer to a commit / where you are now |
| **Reflog** | the history of HEAD; `git reflog` → `git reset --hard <hash>` recovers lost commits |
