"""
Project: Homeschool Lessons (Dream.OS)
File: plugins/teks_daily_training/plugin.py
Purpose: Plugin that generates a TEKS-aligned daily lesson loop for students.
Owner: Local family deployment (homeschool)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LessonItem:
    subject: str
    title: str
    notes: str
    sort_order: int


def plugin_info():
    return {
        "name": "teks_daily_training",
        "version": "0.1.0",
        "capabilities": ["generate_daily_lessons"],
    }


def generate_daily_lessons(db, target_date: str | None = None) -> int:
    """
    Inserts TEKS-aligned items for Charlie (6) and Chris (7) for target_date.
    Only inserts if that student has 0 lessons for that date.
    Returns number of lessons inserted.
    """
    if target_date is None:
        target_date = date.today().isoformat()

    students = db.execute(
        "SELECT id, username, display_name, grade FROM users WHERE is_admin = 0 ORDER BY id"
    ).fetchall()

    inserted = 0
    for s in students:
        existing = db.execute(
            "SELECT COUNT(*) AS c FROM lessons WHERE user_id = ? AND lesson_date = ?",
            (s["id"], target_date),
        ).fetchone()["c"]
        if existing:
            continue

        items: list[LessonItem] = []
        if (s["username"] or "").lower() == "charlie" or s["grade"] == 6:
            # Reading
            passage = (
                "Marcus found a wallet on the ground. No one was around. "
                "He looked inside and saw money and an ID. He paused, then walked toward the office."
            )
            items.append(
                LessonItem(
                    subject="Reading (ELAR)",
                    title="Grade 6: main idea + inference + theme",
                    notes=(
                        "Goal: Find main idea, inference, and theme from a short passage.\n\n"
                        f"Passage:\n{passage}\n\n"
                        "Questions:\n"
                        "1) What is the main idea?\n"
                        "2) What can you infer Marcus is thinking?\n"
                        "3) What is the theme?\n\n"
                        "Practice:\n"
                        "Write two sentences: main idea + inference with evidence.\n\n"
                        "Play: open Practice for quiz-style questions + XP."
                    ),
                    sort_order=10,
                )
            )

            # Math
            items.append(
                LessonItem(
                    subject="Math",
                    title="Grade 6: one-step equation (Practice)",
                    notes=(
                        "Goal: Isolate x in a one-step equation (TEKS-style).\n\n"
                        "Practice:\n"
                        "Solve: x + 7 = 15 (show the step).\n\n"
                        "Play: Practice runs multiple-choice on this skill.\n\n"
                        "Questions:\n"
                        "What inverse operation do you use first?"
                    ),
                    sort_order=20,
                )
            )
            items.append(
                LessonItem(
                    subject="Math",
                    title="Grade 6: coordinate plane (see textbook)",
                    notes=(
                        "Goal: Plot points in all four quadrants.\n\n"
                        "Practice:\n"
                        "Graph the point (3, -2) on a coordinate plane.\n\n"
                        "Play: if Practice shows other Math items, that is OK — same grade band.\n\n"
                        "Questions:\n"
                        "Which quadrant is (3, -2) in?"
                    ),
                    sort_order=30,
                )
            )

        elif (s["username"] or "").lower() == "chris" or s["grade"] == 7:
            # Reading
            passage = "The author describes a storm as “angry and alive,” shaking the town with force."
            items.append(
                LessonItem(
                    subject="Reading (ELAR)",
                    title="Grade 7: purpose, structure, evidence",
                    notes=(
                        "Goal: Explain author’s purpose, text structure, and cite evidence.\n\n"
                        f"Passage:\n{passage}\n\n"
                        "Questions:\n"
                        "1) What is the author’s purpose?\n"
                        "2) What type of text structure is this?\n"
                        "3) What evidence supports your answer?\n\n"
                        "Practice:\n"
                        "One sentence per question above.\n\n"
                        "Play: Practice for grade 7 reading quiz + XP."
                    ),
                    sort_order=10,
                )
            )

            # Math
            items.append(
                LessonItem(
                    subject="Math",
                    title="Grade 7: percent discount (Practice)",
                    notes=(
                        "Goal: Find a sale price after a percent discount.\n\n"
                        "Practice:\n"
                        "A shirt costs $20. It’s 25% off. What is the new price?\n\n"
                        "Play: Practice matches this problem style.\n\n"
                        "Questions:\n"
                        "Could you solve it by paying 75% of $20 instead?"
                    ),
                    sort_order=20,
                )
            )
            items.append(
                LessonItem(
                    subject="Math",
                    title="Grade 7: two-step equations (Practice)",
                    notes=(
                        "Goal: Solve two-step equations with inverse operations.\n\n"
                        "Practice:\n"
                        "Solve: 2x + 5 = 15 (show each step).\n\n"
                        "Play: Practice includes two-step items for XP.\n\n"
                        "Questions:\n"
                        "Why subtract before dividing?"
                    ),
                    sort_order=30,
                )
            )

        else:
            # Unknown student: do nothing (plugin focuses on Charlie/Chris initially)
            continue

        db.executemany(
            "INSERT INTO lessons (user_id, lesson_date, subject, title, notes, sort_order) VALUES (?,?,?,?,?,?)",
            [(s["id"], target_date, i.subject, i.title, i.notes, i.sort_order) for i in items],
        )
        inserted += len(items)

    db.commit()
    return inserted

