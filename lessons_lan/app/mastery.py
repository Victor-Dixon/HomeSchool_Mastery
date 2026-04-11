"""
Project: Homeschool Lessons (Dream.OS)
File: app/mastery.py
Purpose: Mastery gate logic (accuracy, mixed review, boss clears).
Owner: Local family deployment (homeschool)
"""

from __future__ import annotations

from typing import Any


def recent_accuracy(attempts: list[dict[str, Any]], window: int = 12) -> float:
    recent = attempts[-window:]
    if not recent:
        return 0.0
    return sum(1 for a in recent if a.get("correct")) / len(recent)


def mixed_review_clear(attempts: list[dict[str, Any]], window: int = 12) -> bool:
    recent = attempts[-window:]
    if len(recent) < window:
        return False
    subjects = {a.get("subject") for a in recent if a.get("subject")}
    skills = {a.get("skill") for a in recent if a.get("skill")}
    return len(subjects) >= 2 and len(skills) >= 3


def boss_clear(last_boss_score: float | None, minimum: float = 0.8) -> bool:
    return last_boss_score is not None and last_boss_score >= minimum


def can_level_up(student: dict[str, Any]) -> tuple[bool, str]:
    attempts = student.get("attempts") or []
    if recent_accuracy(attempts) < 0.85:
        return False, "Recent accuracy below 85%"
    if not mixed_review_clear(attempts):
        return False, "Mixed review not yet cleared"
    if not boss_clear(student.get("last_boss_score")):
        return False, "Boss fight not cleared"
    return True, "Level up unlocked"
