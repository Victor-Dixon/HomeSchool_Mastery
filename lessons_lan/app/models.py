"""
Project: Homeschool Lessons (Dream.OS)
File: app/models.py
Purpose: Pure data models for mastery engine (no DB wiring).
Owner: Local family deployment (homeschool)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class Question:
    id: str
    subject: str
    grade: int
    teks_tags: list[str]
    skill: str
    difficulty: int
    item_type: str  # mcq, multi_select, ordering, short_response
    prompt: str
    choices: list[str] = field(default_factory=list)
    correct_answer: Any = None
    explanation: str = ""


@dataclass(frozen=True)
class Attempt:
    question_id: str
    student: str
    correct: bool
    score: float
    skill: str
    subject: str
    item_type: str
    was_boss: bool = False


@dataclass
class MasteryState:
    skill: str
    attempts: int = 0
    correct: int = 0
    recent_scores: list[float] = field(default_factory=list)


@dataclass(frozen=True)
class BossResult:
    student: str
    boss_level: int
    subject: str
    score: float
    max_score: float
    passed: bool


@dataclass(frozen=True)
class GearDrop:
    name: str
    slot: str
    rarity: str
    source: str
    description: str = ""
    icon: str = "🧰"


@dataclass
class StudentProfile:
    name: str
    grade: int
    xp: int = 0
    level: int = 1
    title: str = ""
    last_boss_score: Optional[float] = None
