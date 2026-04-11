"""
Project: Homeschool Lessons (Dream.OS)
File: app/grading.py
Purpose: Pure grading helpers for multiple item types.
Owner: Local family deployment (homeschool)
"""

from __future__ import annotations

import json
import re
from typing import Iterable


def grade_multi_select(selected: list[str], correct: list[str]) -> bool:
    return set(selected) == set(correct)


def grade_ordering(student_order: list[str], correct_order: list[str]) -> bool:
    return student_order == correct_order


def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def grade_short_response(answer: str, expected: str | list[str]) -> bool:
    if isinstance(expected, list):
        normalized_expected = {normalize_text(x) for x in expected}
        return normalize_text(answer) in normalized_expected
    return normalize_text(answer) == normalize_text(expected)


def grade_mcq(selected_key: str, answer_key: str) -> bool:
    return normalize_text(selected_key) == normalize_text(answer_key)


def grade_mcq_choice_text(selected_text: str, choices_json: str, answer_key: str) -> bool:
    """True if selected text matches the choice denoted by letter answer_key (A, B, …)."""
    try:
        choices = json.loads(choices_json or "[]")
    except (json.JSONDecodeError, TypeError):
        return False
    if not isinstance(choices, list):
        return False
    key = (answer_key or "").strip().upper()
    if len(key) != 1 or key < "A" or key > "Z":
        return False
    idx = ord(key) - ord("A")
    if idx < 0 or idx >= len(choices):
        return False
    return normalize_text(selected_text) == normalize_text(str(choices[idx]))


def score_boolean(correct: bool) -> float:
    return 1.0 if correct else 0.0


def mean(values: Iterable[float]) -> float:
    vals = list(values)
    if not vals:
        return 0.0
    return sum(vals) / len(vals)
