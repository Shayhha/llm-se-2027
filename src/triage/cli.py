"""Command line: take an issue, print its triage record as JSON.

    uv run python -m triage.cli --split dev --number 3891
    uv run python -m triage.cli --split dev --limit 20 --spread
    uv run python -m triage.cli --file my_issue.json

The sealed split is refused: `test.json` must not be read.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from triage.extract import configure_lm, configured_model, triage
from triage.schema import Issue

SNAPSHOT = Path(__file__).resolve().parents[2] / "data" / "snapshot"
OPEN_SPLITS = ("train", "dev")


def load_split(split: str) -> list[Issue]:
    if split not in OPEN_SPLITS:
        raise SystemExit(f"split must be one of {OPEN_SPLITS}; test.json is sealed")
    raw: list[dict[str, object]] = json.loads((SNAPSHOT / f"{split}.json").read_text(encoding="utf-8"))
    return [Issue.model_validate(item) for item in raw]


def load_file(path: Path) -> list[Issue]:
    data: object = json.loads(path.read_text(encoding="utf-8"))
    items: list[object] = list(data) if isinstance(data, list) else [data]  # type: ignore[arg-type]
    return [Issue.model_validate(item) for item in items]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Triage GitHub issues into structured records.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--split", choices=OPEN_SPLITS, help="read issues from data/snapshot")
    source.add_argument("--file", type=Path, help="a JSON file with one issue or a list of issues")
    parser.add_argument("--number", type=int, help="only the issue with this number")
    parser.add_argument("--limit", type=int, default=1, help="how many issues to triage (default 1)")
    parser.add_argument(
        "--spread",
        action="store_true",
        help="pick --limit issues evenly spaced through the file instead of the first ones "
        "(the snapshot is sorted by repo, so the first 20 are all from one repo)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=4.0,
        help="seconds to wait between issues; the Gemini free tier rate-limits bursts (default 4)",
    )
    args = parser.parse_args(argv)

    load_dotenv()
    model = configured_model()
    configure_lm(model)

    issues = load_split(args.split) if args.split else load_file(args.file)
    if args.number is not None:
        issues = [i for i in issues if i.number == args.number]
        if not issues:
            print(f"no issue #{args.number} found", file=sys.stderr)
            return 1
    if args.spread and len(issues) > args.limit > 0:
        step = len(issues) / args.limit
        issues = [issues[int(i * step)] for i in range(args.limit)]
    for index, issue in enumerate(issues[: args.limit]):
        if index:
            time.sleep(args.delay)
        print(triage(issue, model).model_dump_json(), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
