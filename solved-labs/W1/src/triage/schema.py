"""Typed records for one issue in and one triage record out.

Everything in this module is fully typed. Untyped model output is turned into
these types in `extract.py` and nowhere else.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

IssueType = Literal["bug", "enhancement", "documentation", "question", "meta"]
Severity = Literal["low", "medium", "high", "critical"]

ISSUE_TYPES: tuple[IssueType, ...] = ("bug", "enhancement", "documentation", "question", "meta")
SEVERITIES: tuple[Severity, ...] = ("low", "medium", "high", "critical")


class Issue(BaseModel):
    """The only issue fields the triage step is allowed to see.

    Labels, comments and author are deliberately absent: labels are where the
    gold answers come from, so passing them to the model would leak the answer.
    """

    model_config = ConfigDict(frozen=True, extra="ignore")

    repo: str
    number: int = Field(gt=0)
    title: str
    body: str = ""


class TriageRecord(BaseModel):
    """A validated triage result. Strict: values are rejected, never repaired."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    repo: str
    number: int
    issue_type: IssueType
    component: str | None
    severity: Severity
    has_reproduction_steps: bool
    confidence: float = Field(ge=0.0, le=1.0)
    model: str


class TriageFailure(BaseModel):
    """Emitted when the model gave no valid answer after the retry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    repo: str
    number: int
    reason: str
    raw_output: str = Field(max_length=2000)
    model: str
