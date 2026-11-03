# LLM-SE 2027: all my labs in one repo

Shay Hahiashvili. This one repo holds every lab of the course.

| Lab | Where | Based on |
|---|---|---|
| W1: issue triage (Exercise A) and review of an agent's change (Exercise B) | repo root (`src/triage`, `review-findings.md`, `improvement-log.md`) | [melhadad/llm-se-2027-w1-lab](https://github.com/melhadad/llm-se-2027-w1-lab) |
| W2: lab preparation (OpenSpec install and flawed-spec critique) | `labs/w2/w2-lab-prep.md` | [melhadad/llm-se-2027 `W1/triage-spec-examples`](https://github.com/melhadad/llm-se-2027/tree/main/W1/triage-spec-examples) |
| Later labs | `labs/wN/` | the instructor's repo for that lab |

## Staying in sync with the instructor

The W1 lab is at the root so that the instructor's updates merge without
conflicts:

```
git pull upstream main        # upstream = melhadad/llm-se-2027-w1-lab
```

A lab published as its own repo is added as a subfolder, and later updates to
it are pulled in the same way:

```
git subtree add  --prefix=labs/w3 https://github.com/melhadad/<lab-repo>.git main
git subtree pull --prefix=labs/w3 https://github.com/melhadad/<lab-repo>.git main
```

Each `labs/wN/` keeps its own `pyproject.toml`; run `uv sync` inside it. The
root `pytest` only collects `tests/`, so the labs stay independent.
