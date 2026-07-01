"""
progress.py — Progress Tracking
Saves per-user, per-skill results to a JSON file.
Each Discord user gets their own record keyed by user ID.
"""

import json
import os
from datetime import datetime

DATA_FILE = "data/progress.json"


def _load() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def _save(data: dict):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def record(user_id: str, skill: str, correct: bool):
    """Record a right or wrong answer for a user on a given skill."""
    data = _load()

    if user_id not in data:
        data[user_id] = {}

    if skill not in data[user_id]:
        data[user_id][skill] = {"correct": 0, "wrong": 0, "last_seen": ""}

    if correct:
        data[user_id][skill]["correct"] += 1
    else:
        data[user_id][skill]["wrong"] += 1

    data[user_id][skill]["last_seen"] = datetime.now().strftime("%Y-%m-%d")
    _save(data)


def get_summary(user_id: str) -> dict:
    """Return all skill stats for a user."""
    data = _load()
    return data.get(user_id, {})


def get_weak_skills(user_id: str, threshold: float = 0.5) -> list:
    """
    Return skills where accuracy is below threshold (default 50%).
    These are the skills to drill tomorrow.
    """
    summary = get_summary(user_id)
    weak = []
    for skill, stats in summary.items():
        total = stats["correct"] + stats["wrong"]
        if total > 0:
            accuracy = stats["correct"] / total
            if accuracy < threshold:
                weak.append({
                    "skill": skill,
                    "accuracy": round(accuracy * 100, 1),
                    "correct": stats["correct"],
                    "wrong": stats["wrong"]
                })
    return sorted(weak, key=lambda x: x["accuracy"])


def get_xp(user_id: str) -> int:
    """Calculate total XP: +10 per correct, -0 per wrong (no punishment)."""
    summary = get_summary(user_id)
    return sum(s["correct"] * 10 for s in summary.values())


def get_streak(user_id: str) -> int:
    """Count how many consecutive days the user has answered at least one question."""
    data = _load()
    if user_id not in data:
        return 0

    dates = set()
    for skill_data in data[user_id].values():
        if skill_data.get("last_seen"):
            dates.add(skill_data["last_seen"])

    if not dates:
        return 0

    sorted_dates = sorted(dates, reverse=True)

    streak = 0
    for i, d in enumerate(sorted_dates):
        expected = datetime.now().replace(
            day=datetime.now().day - i
        ).strftime("%Y-%m-%d")
        if d == expected:
            streak += 1
        else:
            break

    return streak
