# Solved labs: Shay Hahiashvili

This repository is a fork of the course repository
[melhadad/llm-se-2027](https://github.com/melhadad/llm-se-2027). Everything outside
`solved-labs/` is the instructor's material, unchanged, and is updated from upstream. All my
lab work lives here, one folder per week.

| Week | Folder | Contents |
|---|---|---|
| W1 | [`W1/`](W1/) | The W1 lab ([melhadad/llm-se-2027-w1-lab](https://github.com/melhadad/llm-se-2027-w1-lab)): environment setup, Exercise A (`src/triage`, tests, `runs/`, `review-findings.md`, `improvement-log.md`, `docs/decisions.md`) and Exercise B (review findings, reading and running) |
| W2 | [`W2/lab-prep/`](W2/lab-prep/) | W2 lab preparation: `openspec --version` and the flawed-spec critique |
| W2 | [`W2/spec-lab/`](W2/spec-lab/) | W2 in-class specifications lab: cycle 1 track B (user stories for CR-1), cycle 2 (OpenSpec: archive `add-issue-triage`, new change `add-security-queue`), answers in `lab/worksheet.md` |

The commit history of each lab was imported with `git subtree`, so the original commits and
their dates are preserved.

## Working on a lab

- **W1** is a self-contained uv project: `cd solved-labs/W1`, `uv sync`, then `uv run pytest`.
  It needs a `.env` in `solved-labs/W1/` (not committed; see `.env.example`).
- **W2 spec lab**: `cd solved-labs/W2/spec-lab` and run `openspec ...` there.
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
