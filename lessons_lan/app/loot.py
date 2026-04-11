"""
Project: Homeschool Lessons (Dream.OS)
File: app/loot.py
Purpose: Gear drop rolls influenced by score (not purely random).
Owner: Local family deployment (homeschool)
"""

from __future__ import annotations

import random
from typing import Any


GEAR_TABLE: dict[str, list[dict[str, str]]] = {
    "common": [
        {"name": "Practice Blade", "slot": "weapon"},
        {"name": "Student Hood", "slot": "helmet"},
    ],
    "uncommon": [
        {"name": "Solver's Shield", "slot": "shield"},
        {"name": "Reader's Boots", "slot": "boots"},
    ],
    "rare": [
        {"name": "Chestplate of Mastery", "slot": "chest"},
        {"name": "Helm of Inference", "slot": "helmet"},
    ],
    "legendary": [
        {"name": "Blade of the Perfect Score", "slot": "weapon"},
    ],
}


def roll_gear(score: float, boss: bool = False) -> dict[str, Any] | None:
    if score < 0.70:
        pool = ["common"]
    elif score < 0.85:
        pool = ["common", "uncommon"]
    elif score < 0.95:
        pool = ["uncommon", "rare"]
    else:
        pool = ["rare"]
        if boss and random.random() < 0.15:
            return {
                **random.choice(GEAR_TABLE["legendary"]),
                "rarity": "legendary",
                "source": "boss",
            }

    rarity = random.choice(pool)
    return {
        **random.choice(GEAR_TABLE[rarity]),
        "rarity": rarity,
        "source": "boss" if boss else "lesson",
    }
