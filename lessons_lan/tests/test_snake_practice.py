"""
Project: Homeschool Lessons (Dream.OS)
File: tests/test_snake_practice.py
Purpose: Snake practice route + JSON API auth and shape.
"""

import json

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "snake.db"
    a = create_app()
    a.config.update(
        TESTING=True,
        SECRET_KEY="test-snake",
        DATABASE=str(db_path),
    )
    with a.app_context():
        from app.db import init_db, seed_if_empty

        init_db()
        seed_if_empty()
    yield a


def login(client, username, password):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)


def test_snake_math_lesson_shows_equation_warden(app):
    c = app.test_client()
    login(c, "charlie", "34086028")
    with app.app_context():
        from app.db import get_db

        db = get_db()
        uid = db.execute("SELECT id FROM users WHERE username='charlie'").fetchone()["id"]
        row = db.execute(
            "SELECT id FROM lessons WHERE user_id = ? AND lower(subject) LIKE '%math%' LIMIT 1",
            (uid,),
        ).fetchone()
        assert row is not None
        lid = row["id"]
    r = c.get(f"/lesson/{lid}/snake")
    assert r.status_code == 200
    assert b"Equation Warden" in r.data
    assert b"Warden" in r.data


def test_snake_page_requires_login(app):
    r = app.test_client().get("/lesson/1/snake")
    assert r.status_code == 302
    assert "/login" in (r.headers.get("Location") or "")


def test_snake_question_endpoint_logged_in(app):
    c = app.test_client()
    login(c, "charlie", "34086028")
    with app.app_context():
        from app.db import get_db

        db = get_db()
        lid = db.execute(
            "SELECT id FROM lessons WHERE user_id = (SELECT id FROM users WHERE username='charlie') LIMIT 1"
        ).fetchone()["id"]
    r = c.get(f"/api/lesson/{lid}/snake-question")
    assert r.status_code == 200
    data = r.get_json()
    assert "prompt" in data
    assert "choices" in data
    assert len(data["choices"]) >= 2
    assert "question_id" in data


def test_snake_answer_records_attempt_and_xp(app):
    c = app.test_client()
    login(c, "charlie", "34086028")
    with app.app_context():
        from app.db import get_db

        db = get_db()
        uid = db.execute("SELECT id FROM users WHERE username='charlie'").fetchone()["id"]
        lid = db.execute(
            "SELECT id FROM lessons WHERE user_id = ? AND subject LIKE '%Math%' LIMIT 1", (uid,)
        ).fetchone()["id"]
        qrow = db.execute(
            "SELECT id, choices_json, answer_key FROM questions WHERE subject = 'Math' LIMIT 1"
        ).fetchone()
        qid = qrow["id"]
        choices = json.loads(qrow["choices_json"])
        key = (qrow["answer_key"] or "A").strip().upper()
        idx = ord(key) - ord("A")
        correct_text = str(choices[idx])

    r = c.post(
        f"/api/lesson/{lid}/snake-answer",
        data=json.dumps(
            {
                "question_id": str(qid),
                "selected_index": idx,
                "selected_text": correct_text,
                "correct": True,
                "teks": "6.7A",
                "skill": "test",
            }
        ),
        content_type="application/json",
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("ok") is True
    assert data.get("correct") is True
    assert data.get("xp_earned") == 10

    with app.app_context():
        from app.db import get_db

        db = get_db()
        n = db.execute(
            "SELECT COUNT(*) AS c FROM question_attempts WHERE user_id = ? AND question_id = ?",
            (uid, qid),
        ).fetchone()["c"]
        assert int(n) >= 1
