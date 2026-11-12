# Solved labs: Shay Hahiashvili

This repository is a fork of the course repository
[melhadad/llm-se-2027](https://github.com/melhadad/llm-se-2027). Everything outside
`solved-labs/` is the instructor's material, unchanged, and is updated from upstream. All my
lab work lives here, one folder per week.

## Repository map

### The instructor's material (unchanged)

| Path | What it is |
|---|---|
| `syllabus-software-engineering-with-ai.md` | The syllabus: weekly topics, labs, readings, grading, project milestones |
| `intro.md` | Lecture notes for the course introduction: GenAI for programming, trust |
| `W1/triage-spec-examples/` | The triage feature written in every spec style: OpenSpec change, SRS (29148), user stories, ADRs, the flawed-spec exercise, and the W2 lab handout (`lab/`) |
| `LLMs/` | Lecture notes on LLM fundamentals: tokenization, transformers, decoding, training, prompting, RAG (from W3) |
| `LLM_Prompting/` | Lecture notes on prompt engineering |
| `dspy/` | DSPy demos and notebooks (a separate uv project) |
| `project/` | Notes for the course project: OpenSpec workflow, Spec-Kit, PRDs, monorepo |
| `media/` | Images used by the notes |

### My work: `solved-labs/`

| Path | What it is |
|---|---|
| [`study-notes/`](study-notes/) | My study notes for the quizzes: [`quiz-w4-prep.md`](study-notes/quiz-w4-prep.md) + [`quiz-w4-cheatsheet.md`](study-notes/quiz-w4-cheatsheet.md) (week-4 quiz: tokenization, next-token prediction, Transformers, decoding + lab 4), [`quiz-w3-prep.md`](study-notes/quiz-w3-prep.md) (week-3 quiz: Foundation Models lecture + W2 lab), [`reading-w1-w2.md`](study-notes/reading-w1-w2.md) (all W1–W2 material, explained), [`quiz-prep-w1-w2.md`](study-notes/quiz-prep-w1-w2.md) (summary + 35 practice questions with answers) and [`labs-practice-guide.md`](study-notes/labs-practice-guide.md) (index of each lab's `PRACTICE.md` + themes across labs) |
| [`W1/`](W1/) | The W1 lab ([melhadad/llm-se-2027-w1-lab](https://github.com/melhadad/llm-se-2027-w1-lab)). **Start with [`W1/TAKEAWAYS.md`](W1/TAKEAWAYS.md); practise with [`W1/PRACTICE.md`](W1/PRACTICE.md).** |
| [`W2/`](W2/) | The W2 lab preparation and the in-class specifications lab. **Start with [`W2/TAKEAWAYS.md`](W2/TAKEAWAYS.md); practise with [`W2/PRACTICE.md`](W2/PRACTICE.md).** |
| [`W3/`](W3/) | The W3 lab (DSPy). The graded copy is the private repo `Shayhha/llm-se-2027-w3-lab-Shayhha`. **Start with [`W3/TAKEAWAYS.md`](W3/TAKEAWAYS.md); practise with [`W3/PRACTICE.md`](W3/PRACTICE.md).** |

### Inside `W1/`

| Path | What it is |
|---|---|
| `src/triage/` | **Exercise A, my implementation**: `schema.py` (the `TriageRecord` contract), `extract.py` (the DSPy call, validation, retry), `cli.py` |
| `tests/triage/` | Exercise A tests (stub LM: valid, invalid-then-valid, invalid twice, hostile title) |
| `runs/` | Output of two 20-issue runs on the dev split |
| `docs/decisions.md` | Every decision taken while building Exercise A, one line each |
| `review-findings.md` | Exercise A surprises, and **Exercise B** review findings (reading vs running, scoring) |
| `improvement-log.md` | Every agent mistake, classified (`capability`/`context`/`tool`/`spec`/`concept`/`bug`) |
| `src/triage_by_agent/`, `exercise-b/`, `tests/exercise_b/` | **Exercise B** material as released: the reference implementation, the agent's diff and its tests |
| `LAB.md`, `README.md`, `tools/`, `config/`, `data/snapshot/` | The instructor's lab handout, setup tools and the frozen issue dataset (`test.json` is sealed until W6) |

### Inside `W2/`

| Path | What it is |
|---|---|
| `lab-prep/w2-lab-prep.md` | The Moodle submission: `openspec --version` and the flawed-spec critique (22 problems + missing topics) |
| `spec-lab/lab/worksheet.md` | **All lab answers**: cycle 1 (INVEST, agent test), cycle 2 (OpenSpec), cycle 3 (routing table, glossary, invariants) |
| `spec-lab/docs/user-stories.md` | Cycle 1: CR-1 written as US-10–US-12, with 5 existing stories updated |
| `spec-lab/openspec/specs/` | Cycle 2: the main specs after archiving `add-issue-triage` |
| `spec-lab/openspec/changes/add-security-queue/` | Cycle 2: my OpenSpec change for CR-1 (proposal + two spec deltas). It validates. |
| `spec-lab/openspec/changes/add-priority-score/`, `add-component-owners/` | Cycle 3: the other teams' in-flight changes (from `lab/in-flight/`) |
| `spec-lab/lab/`, `docs/`, `README.md` (the rest) | The instructor's example folder that the lab works on |

### Inside `W3/`

| Path | What it is |
|---|---|
| `notebooks/w3_lab.ipynb` | **The lab, solved**: every TODO, all outputs, and the answers to the 9 questions |
| `outputs/results/w3_results.json` | The score table per part and per issue |
| `outputs/setup-check-shay-hahiashvili.txt` | The preparation's environment check |
| `docs/decisions.md` | Decisions the lab did not specify (docstring, example, tool depth and limit, …) |
| `improvement-log.md` | Agent and model failures, classified |
| `src/triage_lab/`, `data/`, `tools/`, `README.md`, `SETUP.md` | The instructor's helper code, issue snapshot, source snapshots and handouts |

The commit history of each lab was imported with `git subtree`, so the original commits and
their dates are preserved.

## Working on a lab

- **W1** is a self-contained uv project: `cd solved-labs/W1`, `uv sync`, then `uv run pytest`.
  It needs a `.env` in `solved-labs/W1/` (not committed; see `.env.example`).
- **W2 spec lab**: `cd solved-labs/W2/spec-lab` and run `openspec ...` there.
- **W3** is a uv project with a notebook: `cd solved-labs/W3`, `uv sync`, add `.env`, open `notebooks/w3_lab.ipynb` with the `.venv` kernel.
- **A new week**: create `solved-labs/WN/`, copy in that week's lab material, and commit as you go.

## Staying in sync with the instructor

When the instructor adds new material, pull it in, then push it to the fork:

```
git pull upstream main        # upstream = melhadad/llm-se-2027
git push origin main          # origin   = Shayhha/llm-se-2027 (this fork)
```

(Or use **Sync fork** on the GitHub page, then `git pull origin main`.)

If the instructor updates the separate W1 lab repository:

```
git subtree pull --prefix=solved-labs/W1 https://github.com/melhadad/llm-se-2027-w1-lab.git main
```
