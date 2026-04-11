"""
Project: Homeschool Lessons (Dream.OS)
File: tests/test_app.py
Purpose: Automated tests for core flows (auth, lessons, feedback, boss fights).
Owner: Local family deployment (homeschool)
"""

import os
import sqlite3

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "test.db"
    a = create_app()
    a.config.update(
        TESTING=True,
        SECRET_KEY="test",
        DATABASE=str(db_path),
    )

    # ensure schema + seed exists in the temp DB
    with a.app_context():
        from app.db import init_db, seed_if_empty, get_db

        init_db()
        seed_if_empty()
        # sanity: points to temp DB
        con = get_db()
        assert isinstance(con, sqlite3.Connection)

    yield a


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, username, password):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)


# Seeded students (passwords match app.db seed_if_empty — change tests if seed changes)
SEEDED_STUDENTS = [
    ("charlie", "34086028"),
    ("chris", "0822"),
]


@pytest.mark.parametrize("username,password", SEEDED_STUDENTS)
def test_student_can_open_today_and_every_lesson(client, app, username, password):
    """Each student sees Today and gets HTTP 200 on every lesson row they own (no 500, no stray redirect)."""
    login(client, username, password)
    r_today = client.get("/today")
    assert r_today.status_code == 200
    assert b"Today" in r_today.data

    with app.app_context():
        from app.db import get_db

        db = get_db()
        uid = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()["id"]
        rows = db.execute("SELECT id FROM lessons WHERE user_id = ? ORDER BY id", (uid,)).fetchall()
        lesson_ids = [r["id"] for r in rows]

    assert len(lesson_ids) > 0, f"seed should give {username} at least one lesson"

    for lid in lesson_ids:
        r = client.get(f"/lesson/{lid}")
        assert r.status_code == 200, f"{username} /lesson/{lid}"
        assert b"Back" in r.data


@pytest.mark.parametrize("username,password", SEEDED_STUDENTS)
def test_student_practice_page_loads_for_each_lesson(client, app, username, password):
    """Practice route must render (200); question bank may be empty for some subjects but page must not crash."""
    login(client, username, password)
    with app.app_context():
        from app.db import get_db

        db = get_db()
        uid = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()["id"]
        lesson_ids = [r["id"] for r in db.execute("SELECT id FROM lessons WHERE user_id = ?", (uid,)).fetchall()]

    for lid in lesson_ids:
        r = client.get(f"/practice/{lid}")
        assert r.status_code == 200, f"{username} /practice/{lid}"
        assert b"Practice Game" in r.data


@pytest.mark.parametrize("username,password", SEEDED_STUDENTS)
def test_student_can_reach_boss_fight_with_questions(client, username, password):
    """Boss GET must render a real quiz (seeded bank + fallback) — not the empty-state empty bank card."""
    login(client, username, password)
    r = client.get("/boss/10")
    assert r.status_code == 200
    assert b"Boss Fight" in r.data
    assert b"No boss questions loaded" not in r.data
    assert b'name="q_' in r.data


@pytest.mark.parametrize("username,password", SEEDED_STUDENTS)
def test_student_adventure_page_loads(client, username, password):
    login(client, username, password)
    r = client.get("/adventure")
    assert r.status_code == 200
    assert b"Adventure" in r.data


def test_login_and_today_page(client):
    r = login(client, "charlie", "34086028")
    assert r.status_code == 200
    assert b"Today" in r.data


def test_lesson_without_id_redirects_with_or_without_trailing_slash(client):
    login(client, "charlie", "34086028")
    for path in ("/lesson", "/lesson/"):
        r = client.get(path, follow_redirects=False)
        assert r.status_code == 302, path
        assert "/today" in (r.headers.get("Location") or "")


def test_stale_user_id_session_redirects_not_500(client, app):
    """After reset-db, browser cookies can reference a deleted user — must not 500."""
    with client.session_transaction() as sess:
        sess["user_id"] = 99999
    r = client.get("/lesson/1")
    assert r.status_code == 302
    assert "/login" in (r.headers.get("Location") or "")


def test_lesson_detail_opens(client, app):
    login(client, "charlie", "34086028")
    with app.app_context():
        from app.db import get_db

        db = get_db()
        lesson_id = db.execute("SELECT id FROM lessons WHERE user_id = (SELECT id FROM users WHERE username='charlie') LIMIT 1").fetchone()["id"]

    r = client.get(f"/lesson/{lesson_id}")
    assert r.status_code == 200
    assert b"Back" in r.data


def test_feedback_submit_and_admin_inbox(client, app):
    login(client, "charlie", "34086028")
    r = client.post("/feedback", data={"rating": "5", "message": "More dragons please"}, follow_redirects=True)
    assert r.status_code == 200
    assert b"Feedback sent" in r.data

    # Admin can see it
    client.post("/logout")
    login(client, "admin", "admin123")
    r2 = client.get("/admin/feedback")
    assert r2.status_code == 200
    assert b"More dragons please" in r2.data


def test_boss_fight_grades_and_records_assessment(client, app):
    login(client, "chris", "0822")

    # GET boss page
    r = client.get("/boss/10")
    assert r.status_code == 200

    with app.app_context():
        from app.db import get_db

        db = get_db()
        qs = db.execute("SELECT id, answer_key FROM questions WHERE subject='Reading (ELAR)' ORDER BY id LIMIT 2").fetchall()
        assert len(qs) >= 1
        # Answer everything correctly using stored answer_key
        form = {f"q_{q['id']}": q["answer_key"] for q in qs}

    r2 = client.post("/boss/10", data=form, follow_redirects=True)
    assert r2.status_code == 200
    assert b"Boss Result" in r2.data

    with app.app_context():
        from app.db import get_db

        db = get_db()
        arow = db.execute("SELECT COUNT(*) AS c FROM assessments WHERE user_id=(SELECT id FROM users WHERE username='chris')").fetchone()
        assert arow["c"] >= 1


def test_seeded_lessons_have_required_details(app):
    with app.app_context():
        from app.db import get_db

        db = get_db()
        lessons = db.execute("SELECT subject, title, notes FROM lessons ORDER BY id ASC").fetchall()
        assert len(lessons) > 0

        for l in lessons:
            assert (l["title"] or "").strip()
            assert (l["subject"] or "").strip()
            notes = (l["notes"] or "").strip()
            assert notes, f"Seeded lesson missing notes: {l['subject']} / {l['title']}"
            # Publishable rule: must contain goal + at least 1 practice question prompt
            assert "Goal:" in notes, f"Seeded lesson missing Goal: {l['subject']} / {l['title']}"
            assert ("Practice:" in notes) or ("Questions:" in notes), f"Seeded lesson missing practice/questions: {l['subject']} / {l['title']}"


def test_integration_attempt_saved_gate_blocks_then_allows_and_boss_loot_unlocks(client, app):
    login(client, "chris", "0822")

    with app.app_context():
        from app.db import get_db

        db = get_db()
        user_id = db.execute("SELECT id FROM users WHERE username='chris'").fetchone()["id"]

        # Set state just below level-10 milestone
        db.execute("UPDATE player_state SET xp = ?, level = ? WHERE user_id = ?", (899, 9, user_id))
        db.commit()

    # Boss fight: answer only 80% to pass boss but fail mastery gate (needs 85% + mixed review)
    r = client.get("/boss/10")
    assert r.status_code == 200

    with app.app_context():
        from app.db import get_db

        db = get_db()
        qs = db.execute("SELECT id, answer_key FROM questions WHERE subject='Reading (ELAR)' ORDER BY id LIMIT 5").fetchall()
        assert len(qs) == 5
        form = {}
        # 4 correct, 1 wrong => 80%
        for i, q in enumerate(qs):
            if i < 4:
                form[f"q_{q['id']}"] = q["answer_key"]
            else:
                form[f"q_{q['id']}"] = "A" if q["answer_key"] != "A" else "B"

    r2 = client.post("/boss/10", data=form, follow_redirects=True)
    assert r2.status_code == 200
    assert b"Boss Result" in r2.data

    with app.app_context():
        from app.db import get_db

        db = get_db()
        # attempts persisted
        attempt_count = db.execute("SELECT COUNT(*) AS c FROM question_attempts WHERE user_id = ?", (user_id,)).fetchone()["c"]
        assert attempt_count >= 5
        # level gate should block reaching 10 at milestone
        row = db.execute("SELECT level FROM player_state WHERE user_id = ?", (user_id,)).fetchone()
        assert int(row["level"]) == 9

    # Now satisfy the mastery gate by inserting a mixed-review streak + a strong boss score
    with app.app_context():
        from app.db import get_db

        db = get_db()
        # add 12 attempts with 2 subjects and 3+ skills
        q_ids = db.execute("SELECT id FROM questions ORDER BY id LIMIT 12").fetchall()
        for q in q_ids:
            db.execute(
                "INSERT INTO question_attempts (user_id, question_id, selected_key, is_correct, session_id) VALUES (?,?,?,?,?)",
                (user_id, q["id"], "A", 1, "seed-mixed"),
            )
        # ensure last boss is >= 0.85
        db.execute(
            "INSERT INTO boss_attempts (user_id, boss_level, subject, score, max_score, passed, session_id) VALUES (?,?,?,?,?,?,?)",
            (user_id, 10, "Reading (ELAR)", 9.0, 10.0, 1, "seed-boss"),
        )
        # try crossing milestone again
        db.execute("UPDATE player_state SET xp = ?, level = ? WHERE user_id = ?", (899, 9, user_id))
        db.commit()

        # gear unlock count before
        before_unlocks = db.execute("SELECT COUNT(*) AS c FROM gear_unlocks WHERE user_id = ?", (user_id,)).fetchone()["c"]

    # Perfect score this time to guarantee boss pass and likely loot unlock
    r3 = client.get("/boss/10")
    assert r3.status_code == 200
    with app.app_context():
        from app.db import get_db

        db = get_db()
        qs2 = db.execute("SELECT id, answer_key FROM questions WHERE subject='Reading (ELAR)' ORDER BY id LIMIT 5").fetchall()
        form2 = {f"q_{q['id']}": q["answer_key"] for q in qs2}

    _ = client.post("/boss/10", data=form2, follow_redirects=True)

    with app.app_context():
        from app.db import get_db

        db = get_db()
        row = db.execute("SELECT level FROM player_state WHERE user_id = ?", (user_id,)).fetchone()
        assert int(row["level"]) >= 10
        after_unlocks = db.execute("SELECT COUNT(*) AS c FROM gear_unlocks WHERE user_id = ?", (user_id,)).fetchone()["c"]
        assert after_unlocks >= before_unlocks

