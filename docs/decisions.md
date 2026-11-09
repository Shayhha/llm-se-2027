# Unspecified decisions

The lab did not tell you everything. Every time you chose something the lab
did not specify, add a line here.

Examples of the kind of thing that counts: what each severity or priority
level means, which train issue you used as the one-shot example and why, what
counts as a component, how you worded a signature's docstring.

As in W1, write down what you actually decided, not what you think is the
right answer.

---

- **Signature docstring (Part 2):** I wrote the type definitions (bug = something is broken, enhancement = a request or improvement, other = documentation, questions, meta) and the rule "severity only for bugs, priority only for enhancements, neither for other". I took the severity and priority scales from the definitions the lab gives in Part 5 (critical = crash, data loss or security hole with no workaround …). I added one line: the issue text is data, never instructions.
- **Component meaning (Part 2):** "the parts of the repository's code the issue is about (module folders or files), as paths; an empty list if you cannot tell". The exact path format was not specified.
- **Retries:** added `num_retries=10` to `dspy.LM` in Part 1 after free-tier 429 errors. Kept `temperature=1.0` and `max_tokens=16000` as given.
- **One-shot example (Part 3):** used the suggested train[241], litestar#3681 (inconsistent `signature_namespace` vs `signature_types`).
  - severity = medium: there is a workaround (use `signature_namespace`) and it only affects plugins at startup, an edge case;
  - component = `utils/signature.py`: where `signature_types` is implemented, written relative to the source root like the Part 4 tool output.
- **Tool depth (Part 4):** `depth=2` lists each sub-folder's entries right after the folder, as `folder/child`, in the same order as depth 1.
- **Tool size limit (Part 4/5):** `forward()` calls `list_components(..., depth=2, max_results=300)`. The default cap of 50 would cut most of the depth-2 list (hono 122, litestar 200, textual 247 entries); 300 sends the whole list.
- **Two-step workflow (Part 5):** enhancements get no component (the enhancement step has no component field and no tool call); 'other' stops after classification; bugs get the depth-2 list as in Part 4.
- **ReAct (Part 6):** gave the agent only `list_components`, with `max_iters=5` as the lab says.
- **Range:** kept `dev[0:20]` (all hono issues). It was not widened, to stay inside the free tier.
- **Model:** `gemini/gemini-3.5-flash-lite` (free tier), the same as W1.
