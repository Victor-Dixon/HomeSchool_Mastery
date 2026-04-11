"""
Project: Homeschool Lessons (Dream.OS)
File: app/rpg.py
Purpose: RPG progression helpers (XP/leveling and boss selection).
Owner: Local family deployment (homeschool)
"""

from __future__ import annotations

from datetime import date
from typing import Any

from .db import get_db
from .mastery import can_level_up


def ensure_player_state(user_id: int):
    db = get_db()
    db.execute("INSERT OR IGNORE INTO player_state (user_id) VALUES (?)", (user_id,))
    db.commit()


def add_xp(user_id: int, amount: int):
    if amount <= 0:
        return
    db = get_db()
    ensure_player_state(user_id)
    row = db.execute("SELECT xp, level FROM player_state WHERE user_id = ?", (user_id,)).fetchone()
    xp = int(row["xp"]) + int(amount)
    level = int(row["level"])

    # simple leveling curve: level up every 100xp
    new_level = max(1, xp // 100 + 1)

    # Mastery gates (V1):
    # Only enforce at milestone levels (10, 20, 30...). This avoids locking early progression
    # while still requiring skill evidence + boss clearance before major rank-ups.
    if new_level > level:
        snapshot = build_student_gate_snapshot(user_id)
        ok, _reason = can_level_up(snapshot)
        if not ok:
            next_milestone = ((level // 10) + 1) * 10
            if new_level >= next_milestone:
                new_level = min(new_level, next_milestone - 1)

    db.execute(
        "UPDATE player_state SET xp = ?, level = ?, updated_at = datetime('now') WHERE user_id = ?",
        (xp, new_level, user_id),
    )
    db.commit()


def get_next_boss_level(level: int) -> int:
    # Boss every 10 levels
    if level < 10:
        return 10
    return ((level // 10) + (0 if level % 10 == 0 else 1)) * 10


def snake_question_subject_for_lesson(lesson_subject: str) -> str:
    """
    Canonical questions.subject for Snake (must match boss domains: Math vs Reading).
    """
    s = (lesson_subject or "").lower()
    if "math" in s:
        return "Math"
    if "read" in s or "elar" in s or "ela" in s:
        return "Reading (ELAR)"
    stripped = (lesson_subject or "").strip()
    return stripped if stripped else "Math"


def snake_opponent_for_lesson(lesson_subject: str) -> dict[str, str]:
    """
    Snake UI + opponent flavor. Math lessons face the Equation Warden (same identity as the Math boss arc).
    """
    qs = snake_question_subject_for_lesson(lesson_subject)
    if qs == "Math":
        return {
            "boss_id": "equation_warden",
            "boss_name": "Equation Warden",
            "arena_name": "The Warden's Grid",
            "intro_lead": "The Equation Warden seals every problem into colored orbs.",
            "intro_detail": (
                "Steer into the orb that solves the riddle. Wrong answers feed the Warden a life from you."
            ),
            "page_title": "Equation Warden",
            "emoji": "⚖️",
        }
    if qs == "Reading (ELAR)":
        return {
            "boss_id": "reading_dragon",
            "boss_name": "Reading Dragon",
            "arena_name": "The Dragon's Coil",
            "intro_lead": "The Reading Dragon circles the board with evidence and meaning.",
            "intro_detail": "Only the true answer orb lets your snake grow. Mistakes cost a life.",
            "page_title": "Reading Dragon",
            "emoji": "🐉",
        }
    return {
        "boss_id": "guardian",
        "boss_name": "Practice Guardian",
        "arena_name": "Training Grounds",
        "intro_lead": "Pick up the correct answer orb before your lives run out.",
        "intro_detail": "Use arrow keys or WASD. Wrong answers cost a life.",
        "page_title": "Snake Practice",
        "emoji": "🛡️",
    }


def pick_boss_subject(user_row) -> str:
    """
    Very simple v1: alternate Reading/Math bosses by boss level.
    Later: choose based on weakest TEKS strand/skill graph.
    """
    # For Chris: prioritize Reading first (the "Reading Dragon" arc)
    username = (user_row["username"] or "").lower()
    if username == "chris":
        return "Reading (ELAR)"
    return "Math" if (user_row["grade"] or 0) % 2 == 0 else "Reading (ELAR)"


def build_student_gate_snapshot(user_id: int, *, window: int = 12) -> dict[str, Any]:
    """
    Builds the minimal dict expected by app.mastery.can_level_up() from DB state.
    Uses recent question attempts and latest boss score ratio.
    """
    db = get_db()
    rows = db.execute(
        """
        SELECT qa.is_correct, q.subject, q.skill
        FROM question_attempts qa
        JOIN questions q ON q.id = qa.question_id
        WHERE qa.user_id = ?
        ORDER BY qa.id ASC
        """,
        (user_id,),
    ).fetchall()

    attempts: list[dict[str, Any]] = [
        {"correct": bool(r["is_correct"]), "subject": r["subject"], "skill": r["skill"]} for r in rows
    ]

    last_boss = db.execute(
        """
        SELECT score, max_score
        FROM boss_attempts
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,),
    ).fetchone()

    last_boss_score = None
    if last_boss is not None and float(last_boss["max_score"] or 0.0) > 0:
        last_boss_score = float(last_boss["score"] or 0.0) / float(last_boss["max_score"] or 1.0)

    return {
        "attempts": attempts[-window:],
        "last_boss_score": last_boss_score,
        "assessed_on": date.today().isoformat(),
    }

