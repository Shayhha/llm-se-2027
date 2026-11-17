# Quiz W4 cheat sheet

`text ─encode─► IDs ─LM─► p(next token) ─decoding─► token ─repeat until [EOS]─► decode ─► text`

**Tokenization (01)**

| | |
|---|---|
| **Tokenizer** | string ↔ list of integer token IDs (encode / decode); deterministic, invertible |
| **Why** | numbers for the network · a manageable vocabulary · no unknown words |
| **V / L** | vocabulary size (30k–100k+) / max tokens at once (longer input is truncated) |
| **Goal** | the fewest tokens for vocabulary ≤ V |
| **Sub-word** | learn-ing, micro+processor, Kuber+net+es |
| **BPE** | merge the most frequent adjacent pair, repeat until size V (`e`+`s`→`es`) |

**Language model (02)**

| | |
|---|---|
| **LM** | p(next token \| previous tokens); chain rule → a generative model |
| **Train / evaluate** | cross-entropy / perplexity (lower = better) |
| **Bengio** | word vectors + prediction learned together (representation learning) |
| **Transformer** | self-attention = a weighted mix of all tokens; positional embeddings (RoPE) |

**Decoding (03 + HF)**

| | |
|---|---|
| **Greedy** | the top token each step; not the best sequence; repetitive |
| **Beam** | keep the best sequences; good for translation, dull for stories |
| **Sampling** | random by probability; varied, can be incoherent |
| **Temperature** | low = sharp (→0 = greedy), high = creative |
| **Top-k / top-p** | k best tokens (fixed) / the smallest set with probability > p (adapts) |
| **HF conclusion** | top-k/top-p more fluent; repetition from training; no one-size-fits-all |
| **Speculative** | a small model drafts, the big one verifies: faster, same output |

**Training (04, 05)**: pre-training (self-supervised) → **SFT** (instruction, answer) →
**RLHF** (reward model + PPO) → **reasoning RL**. **LoRA** = freeze + train small matrices
(W + B×A). **Instruction tuning** → zero-shot on new tasks.

**Prompting (06)**

| | |
|---|---|
| **Prompting strategy** | inference-time algorithm, no weight updates |
| **ICL** | learn from prompt examples without training; order and choice matter |
| **Why decompose** | cost O((P+A)²), so split complex tasks |
| **CoT** | step-by-step reasoning |
| **PoT** | write a program, execute it externally |
| **ReAct** | interleave reasoning + tool actions |
| **Self-consistency** | many reasoning paths → majority answer |
| **Tools / MCP** | delegate sub-tasks to tools / the standard tool protocol |

**RAG (06.5)**

| | |
|---|---|
| **RAG** | retrieve documents into the prompt → grounded answers |
| **Why** | parametric memory is static and stale → hallucination |
| **Pipeline** | index: chunks → embeddings → vector DB · query: embed → top-k (cosine) → LLM |
| **Parts** | knowledge base, encoder, retriever (+ re-ranker), generator |
| **Risks** | lost in the middle, retrieval noise, prompt injection, latency |
| **Metrics** | Precision/Recall@k, MRR, nDCG, faithfulness, answer relevance |

**DSPy**

| | |
|---|---|
| **Signature** | typed inputs and outputs; the docstring is the instruction |
| **Predict / ChainOfThought** | one LLM call / one call with reasoning first |
| **Example + .demos** | few-shot examples |
| **Module + forward()** | a multi-step program |
| **ReAct** | an agent loop: thought → tool → observation |
| **Optimizer** | BootstrapFewShot picks demos with a metric + train set |
