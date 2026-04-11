from app.generator import generate_lesson


def test_generate_lesson_prefers_weak_skills():
    bank = [
        {"id": "1", "grade": 6, "skill": "fractions", "subject": "math"},
        {"id": "2", "grade": 6, "skill": "fractions", "subject": "math"},
        {"id": "3", "grade": 6, "skill": "ratios", "subject": "math"},
        {"id": "4", "grade": 6, "skill": "inference", "subject": "reading"},
        {"id": "5", "grade": 6, "skill": "main_idea", "subject": "reading"},
    ]

    lesson = generate_lesson(
        question_bank=bank,
        grade=6,
        student_name="Charlie",
        weak_skills={"fractions": 3},
        size=4,
    )

    assert lesson["student"] == "Charlie"
    assert lesson["grade"] == 6
    assert len(lesson["questions"]) <= 4
    assert any(q["skill"] == "fractions" for q in lesson["questions"])
