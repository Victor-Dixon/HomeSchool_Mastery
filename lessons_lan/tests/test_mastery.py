from app.mastery import can_level_up


def test_level_up_blocked_without_accuracy():
    student = {
        "attempts": [{"correct": False, "subject": "math", "skill": "fractions"}] * 12,
        "last_boss_score": 1.0,
    }
    ok, reason = can_level_up(student)
    assert ok is False
    assert "accuracy" in reason.lower()


def test_level_up_blocked_without_mixed_review():
    student = {
        "attempts": [{"correct": True, "subject": "math", "skill": "fractions"}] * 12,
        "last_boss_score": 1.0,
    }
    ok, reason = can_level_up(student)
    assert ok is False
    assert "mixed" in reason.lower()


def test_level_up_blocked_without_boss_clear():
    attempts = []
    for i in range(6):
        attempts.append({"correct": True, "subject": "math", "skill": f"m{i}"})
    for i in range(6):
        attempts.append({"correct": True, "subject": "reading", "skill": f"r{i}"})

    student = {
        "attempts": attempts,
        "last_boss_score": 0.79,
    }
    ok, reason = can_level_up(student)
    assert ok is False
    assert "boss" in reason.lower()


def test_level_up_allowed_when_all_gates_clear():
    attempts = []
    for i in range(6):
        attempts.append({"correct": True, "subject": "math", "skill": f"m{i}"})
    for i in range(6):
        attempts.append({"correct": True, "subject": "reading", "skill": f"r{i}"})

    student = {
        "attempts": attempts,
        "last_boss_score": 0.90,
    }
    ok, reason = can_level_up(student)
    assert ok is True
    assert "level up" in reason.lower()

import pytest
from app.mastery import recent_accuracy, mixed_review_clear, boss_clear


def varied_attempts(count=12):
    return [{"correct": True, "subject": ("math", "reading")[i % 2],
             "skill": ("fractions", "inference", "equations")[i % 3]}
            for i in range(count)]


@pytest.mark.parametrize("correct,allowed", [(10, False), (11, True), (12, True)])
def test_accuracy_gate_at_default_window(correct, allowed):
    attempts = varied_attempts()
    for i in range(12 - correct):
        attempts[i]["correct"] = False
    assert can_level_up({"attempts": attempts, "last_boss_score": 0.8})[0] is allowed


def test_recent_window_excludes_older_attempts():
    older = [{"correct": False, "subject": "old", "skill": "old"}] * 20
    assert recent_accuracy(older + varied_attempts()) == 1.0
    assert recent_accuracy([]) == 0.0
    assert not mixed_review_clear(varied_attempts(11))
    assert mixed_review_clear(varied_attempts())


@pytest.mark.parametrize("subjects,skills,allowed", [(1, 3, False), (2, 2, False), (2, 3, True)])
def test_mixed_review_diversity_boundaries(subjects, skills, allowed):
    attempts = [{"correct": True, "subject": str(i % subjects),
                 "skill": str(i % skills)} for i in range(12)]
    assert mixed_review_clear(attempts) is allowed
    assert can_level_up({"attempts": attempts, "last_boss_score": 1.0})[0] is allowed


@pytest.mark.parametrize("score,allowed", [(None, False), (0.799, False), (0.8, True), (1.0, True)])
def test_boss_score_boundary(score, allowed):
    assert boss_clear(score) is allowed
    assert can_level_up({"attempts": varied_attempts(), "last_boss_score": score})[0] is allowed
