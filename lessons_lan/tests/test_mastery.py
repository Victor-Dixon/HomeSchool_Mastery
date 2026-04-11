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
