"""
Project: Homeschool Lessons (Dream.OS)
File: app/generator.py
Purpose: Dynamic lesson generator (adaptive selection from a question bank).
Owner: Local family deployment (homeschool)
"""

from __future__ import annotations

import random
from typing import Any


def generate_lesson(
    question_bank: list[dict[str, Any]],
    grade: int,
    student_name: str,
    weak_skills: dict[str, int],
    size: int = 8,
) -> dict[str, Any]:
    eligible = [q for q in question_bank if q.get("grade") == grade]

    weak_first: list[dict[str, Any]] = []
    other: list[dict[str, Any]] = []

    weak_skill_names = set((weak_skills or {}).keys())

    for q in eligible:
        if q.get("skill") in weak_skill_names:
            weak_first.append(q)
        else:
            other.append(q)

    random.shuffle(weak_first)
    random.shuffle(other)

    selected = (weak_first[: max(3, size // 2)] + other)[:size]

    return {
        "student": student_name,
        "grade": grade,
        "title": f"Adaptive Lesson for {student_name}",
        "questions": selected,
    }
