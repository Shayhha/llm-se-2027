# Quiz W4 cheat sheet

`text â”€encodeâ”€â–º token IDs â”€LMâ”€â–º p(next token) â”€decodingâ”€â–º token â”€repeat until [EOS]â”€â–º decode â”€â–º text`

## Tokenization (01)

| Concept | Meaning |
|---|---|
| **Tokenization** | the critical first step: break raw text into tokens; the LLM operates only on tokens |
| **Tokenizer** | a function mapping a string of text â†’ a list of integers |
| **Encode / decode** | tokenize: text â†’ token IDs; detokenize: token IDs â†’ text |
| **Why** | (1) numerical conversion â†’ embedding vectors; (2) a manageable vocabulary size; (3) handling unknown (OOV) words |
| **Vocabulary size V** | the number of unique tokens; a hyper-parameter, ~30kâ€“100k+; bigger = common words in 1 token, but a bigger model |
| **Max context length L** | the maximum tokens at once (4096, 8192, â€¦); longer input is truncated |
| **Objective** | minimize Î£ Tokens(Sentenceáµ¢) subject to VocabularySize â‰¤ V: the fewest tokens, still semantically rich |
| **Constraint** | invertible + deterministic: Detokenize(Tokenize(s)) = s; Tokenize(Detokenize(t)) = t |
| **Sub-word** | inflections (learn-ing), composites (micro+processor), OOV (Kuber+net+es instead of `<UNK>`) |
| **BPE** | iterative compression: start from characters â†’ merge the most frequent adjacent pair â†’ until size V (used in GPT-3) |
| **BPE example** | `e`+`s` â†’ `es`, then `es`+`t` â†’ `est`; `lowering` â†’ l o w er i n g |
| **Pre-split** | text is first split into space-separated sequences with regexps |

## Language model (02)

| Concept | Meaning |
|---|---|
| **LM** | a probabilistic function [tâ‚€â€¦tâ‚™â‚‹â‚] â†’ p(tâ‚™ \| t<n): a distribution over the next token |
| **Chain rule** | p(tâ‚€â€¦tâ‚™) = p(tâ‚€)Â·p(tâ‚â€¦tâ‚™ \| tâ‚€), so a distribution over all sequences: a **generative model** |
| **Objective** | Lâ‚(U) = Î£ log p(uáµ¢ \| uáµ¢â‚‹â‚–â€¦uáµ¢â‚‹â‚; Î¸), with k = context window: **cross-entropy** |
| **Perplexity** | the evaluation metric: uncertainty in predicting a test corpus (lower = better) |
| **n-grams** | the classic LMs (1970sâ€“2000s); generalize by concatenating short seen sequences |
| **Bengio 2000** | fight the **curse of dimensionality** by learning a **distributed representation** per word together with the sequence probability function |
| **Representation learning** | similar words â†’ nearby vectors, so unseen sentences of similar words get high probability |
| **Better than humans** | LMs beat humans at next-token prediction (top-1 accuracy, perplexity) |
| **GPT equations** | hâ‚€ = UÂ·Wâ‚‘ + Wâ‚š â†’ hâ‚— = transformer_block(hâ‚—â‚‹â‚) â†’ p(u) = softmax(hâ‚™Â·Wâ‚‘áµ€) |
| **Wâ‚‘ / Wâ‚š / softmax** | token embedding matrix / position embedding matrix / V scores â†’ a probability distribution |

## Transformer (02.5)

| Concept | Meaning |
|---|---|
| **Transformer** | Vaswani et al. 2017; replaced RNNs, LSTMs, GRUs |
| **Positional embeddings** | needed because self-attention ignores order: sinusoidal, learned, **RoPE** (most common) |
| **Attention** | the mutual influence of tokens: each token = a weighted combination of its neighbours |
| **Self-attention formula** | Q = XW_Q, K = XW_K, V = XW_V; softmax(QKáµ€/âˆšd_k)Â·V; **multi-head** = several in parallel |
| **Block** | attention â†’ layer norm (zero mean, unit variance) â†’ feed-forward (2 linear + ReLU) â†’ residual (add the input back) |
| **Final output** | linear + softmax â†’ a distribution over the vocabulary |

## Decoding (03 + Hugging Face "How to generate")

| Concept | Meaning |
|---|---|
| **Auto-regressive** | generate tâ‚, append, generate tâ‚‚, â€¦ until **[EOS]**; the length isn't fixed |
| **Greedy** | the highest-probability token each step; not the most probable sequence; repetitive |
| **Beam search** (`num_beams`) | keep the most likely sequences; good for predictable length (translation, summarization) |
| **n-gram penalty** (`no_repeat_ngram_size`) | no n-gram twice; careful ("New York") |
| **Sampling** (`do_sample`) | random according to probability; non-deterministic, may be incoherent |
| **Temperature** | low â†’ sharper distribution; â†’ 0 = greedy |
| **Top-k** (`top_k`) | sample among the k most likely; fixed k, doesn't adapt |
| **Top-p / nucleus** (`top_p`) | the smallest set with cumulative probability > p; adapts |
| **API parameters** | usually top-p and temperature |
| **HF conclusion** | top-p/top-k are more fluent for open-ended text; repetition comes from the model's training; no one-size-fits-all |
| **Degeneration** (Holtzman) | likelihood decoding â†’ bland, repetitive; nucleus cuts the unreliable tail |
| **Beam search & UID** (Meister) | beam works by enforcing uniform information density |
| **Non-termination** (Choi) | decoding can repeat, never stop, or stop too early |
| **Unlikelihood** (Welleck) | the training objective is at fault; lower the probability of repeats |
| **Î·-sampling** (Hewitt) | truncation = desmoothing; an entropy-dependent threshold |
| **Speculative decoding** | a fast draft model + parallel verification: 2â€“3Ã— faster, identical output; used in production |

## Pre-training and fine-tuning (04)

| Concept | Meaning |
|---|---|
| **Pre-training** | train on self-supervised tasks, then reuse the model for downstream tasks |
| **Self-supervision** | tasks with no manual labels (next / masked word, perturbation removal); raw text is abundant |
| **Fine-tuning** | supervised training of a pre-trained model on a small labelled set; 100 examples â‰ˆ 10,000 from scratch |
| **Fine-tuning objective** | p(y\|x) = softmax(hÂ·W_y); Lâ‚‚ = Î£ log P(y\|x); Lâ‚ƒ = Lâ‚‚ + Î»Â·Lâ‚ (task + next-word) |
| **ULMFiT** | one model fine-tuned on 6 tasks; state of the art with 100Ã— less data |
| **T5 text-to-text** | every task as text with a task prefix, so one cross-entropy loss; multi-task needs scale (C4) |
| **Task scaling** | 6 â†’ 25 â†’ 60 â†’ 1,600 â†’ 1,800 (FLAN) â†’ 2,000 (OPT-IML) tasks |
| **LoRA (PEFT)** | freeze the base, train small low-rank matrices, W + BÃ—A; cheap, avoids catastrophic forgetting, swappable adapters |
| **Instruction fine-tuning** | tasks phrased as instructions (FLAN, InstructGPT) â†’ zero-shot on unseen tasks |
| **InstructGPT** | demonstrations + RL from human feedback; 1.3B preferred over 175B GPT-3 |

## Post-training: the 4 stages (05)

| Stage | Meaning |
|---|---|
| **1. Pre-training** | self-supervised next-token prediction â†’ language foundation + world knowledge |
| **2. SFT** | (instruction, ideal output) pairs â†’ follows instructions; a next-word predictor becomes an assistant |
| **3. RLHF** | a reward model from human rankings + RL (PPO) â†’ helpful, honest, safe |
| **4. Reasoning RL** | process-based rewards â†’ multi-step reasoning; makes CoT, tools and PoT effective |

## Prompting strategies (06)

| Concept | Meaning |
|---|---|
| **Prompting strategy** | an inference-time algorithm (no weight updates): encodes the task in prompts, sets sampling, computes the answer |
| **Zero / one / few-shot** | 0 / 1 / a few examples in the prompt |
| **In-context learning** | learns from prompt examples without weight updates; example order and choice matter (â†’ prompt optimization) |
| **Min 2022** | correct labels barely matter; the label space, input distribution and format drive ICL |
| **Why decompose** | generation costs O((P+A)Â²) (quadratic attention), so complex tasks need more steps |
| **Chain solutions** | generate the sub-steps at once (CoT, PoT) |
| **Successive prompting** | alternate question decomposition and question answering over turns (ReAct) |
| **Scratchpad / CoT** | write intermediate steps; CoT emerges in large models (540B, GSM8K) |
| **PoT** | write a program and execute it externally; computation separated from reasoning (+12% vs CoT) |
| **ReAct** | interleave reasoning and actions (e.g. a Wikipedia API); less hallucination |
| **Self-consistency** | sample many reasoning paths â†’ majority answer (+17.9% GSM8K) |
| **Verifier** | checks candidate answers (trained verifier, or a calculator for arithmetic) |
| **Toolformer** | the LM teaches itself which API to call, when, with which arguments |
| **MCP** | Anthropic's protocol for sharing and discovering tools; CoT/PoT = agent planning |

## RAG (06.5)

| Concept | Meaning |
|---|---|
| **RAG** | add retrieved documents to the prompt â†’ answers grounded in external, up-to-date facts |
| **Parametric memory** | knowledge in the weights: static, stale â†’ hallucination on private or recent data |
| **Two phases** | indexing (offline) Â· retrieval & generation (online) |
| **Knowledge base / vector DB** | documents as embeddings (or a BM25 index) |
| **Encoder** | an embedding model (e.g. Sentence Transformer) for chunks and queries |
| **Retriever / re-ranker** | top-k chunks by cosine similarity / better ordering |
| **Generator** | the LLM: query + chunks â†’ grounded answer |
| **Advanced** | chunking (semantic, recursive), HyDE, cross-encoder re-ranking, Graph RAG, Self-RAG |
| **Risks** | lost in the middle, retrieval noise, prompt injection, latency |
| **Retrieval metrics** | Precision@k, Recall@k, MRR, nDCG |
| **Generation metrics** | faithfulness (groundedness), answer relevance, context recall (LLM-as-a-judge; RAGAs, ARES) |
| **Origin** | Lewis et al. 2020: seq2seq + Dense Passage Retriever (DPR) |

## Lab 4: git (provisional)

| Concept | Meaning |
|---|---|
| **Content-addressed** | objects are named by the hash of their content; immutable |
| **Blob / tree / commit** | file content / directory / tree + parents + message |
| **`hash-object` / `cat-file`** | content â†’ blob / read an object |
| **`write-tree` / `commit-tree`** | index â†’ tree / tree â†’ commit |
| **Ref / HEAD** | a mutable pointer (branch) / the current position; detached = points at a commit |
| **Reflog** | the history of HEAD; `git reset --hard <hash>` recovers lost commits |
