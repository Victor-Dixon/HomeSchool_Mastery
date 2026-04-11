"""
Project: Homeschool Lessons (Dream.OS)
File: tests/test_lesson_pages.py
Purpose: Regression tests — lesson URLs must render (no 500) and `/lesson` must not 404.
Owner: Local family deployment (homeschool)
"""

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "lesson_pages.db"
    a = create_app()
    a.config.update(
        TESTING=True,
        SECRET_KEY="test-lesson-pages",
        DATABASE=str(db_path),
    )
    with a.app_context():
        from app.db import init_db, seed_if_empty

        init_db()
        seed_if_empty()
    yield a


def login(client, username, password):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)


def test_today_shows_lesson_title_link_not_dead_open_button(app):
    """Open button was redundant / confusing on tablets; title is the link to full lesson."""
    c = app.test_client()
    login(c, "charlie", "34086028")
    r = c.get("/today")
    assert r.status_code == 200
    body = r.data.decode("utf-8", errors="replace")
    assert "/lesson/" in body
    assert ">Open<" not in body
    assert "Practice" in body


def test_lesson_without_id_redirects_to_today_not_404_or_500(app):
    c = app.test_client()
    login(c, "charlie", "34086028")
    r = c.get("/lesson")
    assert r.status_code == 302
    assert "/today" in (r.headers.get("Location") or "")


def test_lesson_without_id_anonymous_goes_to_login(app):
    r = app.test_client().get("/lesson")
    assert r.status_code == 302
    assert "/login" in (r.headers.get("Location") or "")


def test_lesson_ai_chat_round_trip(app, monkeypatch):
    def fake_chat(messages, **kwargs):
        assert any(m.get("role") == "system" for m in messages)
        return ("Short coach reply.", True)

    monkeypatch.setattr("app.routes.ollama_chat", fake_chat)

    c = app.test_client()
    login(c, "charlie", "34086028")
    with app.app_context():
        from app.db import get_db

        db = get_db()
        lid = db.execute(
            "SELECT id FROM lessons WHERE user_id = (SELECT id FROM users WHERE username='charlie') LIMIT 1"
        ).fetchone()["id"]

    r = c.post(
        f"/lesson/{lid}/ai-chat",
        json={"message": "What is the goal?"},
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("reply") == "Short coach reply."
    assert data.get("offline") is False

    r2 = c.get(f"/lesson/{lid}")
    assert r2.status_code == 200
    assert b"Short coach reply." in r2.data


def test_all_seeded_lessons_render_200_for_each_student(app):
    """Every lesson row for charlie/chris must render the lesson template without error."""
    for username, password in (("charlie", "34086028"), ("chris", "0822")):
        c = app.test_client()
        login(c, username, password)
        with app.app_context():
            from app.db import get_db

            db = get_db()
            uid = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()["id"]
            ids = [r["id"] for r in db.execute("SELECT id FROM lessons WHERE user_id = ?", (uid,)).fetchall()]
        assert ids, f"expected seeded lessons for {username}"
        for lid in ids:
            r = c.get(f"/lesson/{lid}")
            assert r.status_code == 200, f"{username} /lesson/{lid} got {r.status_code}"
            body = r.data
            assert b"Practice" in body
            assert b"/snake" in body
            assert b"/games" in body
            assert b"AI lesson coach" in body
            assert b"Back" in body
            assert b"Mark done" in body or b"Done" in body


def test_lesson_primary_mode_prefers_game_notes_over_arbitrary_id(app):
    """game:text-detective / game:discount-dash in notes should not depend on lesson row id."""
    from app.routes import _lesson_primary_mode

    assert (
        _lesson_primary_mode({"id": 9999, "notes": "game:text-detective\nextra", "title": "Any title"})
        == "text_detective"
    )
    assert (
        _lesson_primary_mode({"id": 9999, "notes": "Prefix|game:discount-dash", "title": "Shop"})
        == "discount_dash"
    )


def test_seeded_chris_lessons_carry_game_markers(app):
    """Fresh seed attaches markers so Chris reading / percent rows are stable if ids change."""
    with app.app_context():
        from app.db import get_db

        db = get_db()
        uid = db.execute("SELECT id FROM users WHERE username = ?", ("chris",)).fetchone()["id"]
        rows = db.execute(
            "SELECT notes FROM lessons WHERE user_id = ? ORDER BY sort_order ASC, id ASC",
            (uid,),
        ).fetchall()
    notes_blob = "\n".join((r["notes"] or "") for r in rows)
    assert "game:text-detective" in notes_blob
    assert "game:discount-dash" in notes_blob


def test_lesson_detail_renders_notes_and_title_from_db(app):
    c = app.test_client()
    login(c, "charlie", "34086028")
    with app.app_context():
        from app.db import get_db

        db = get_db()
        row = db.execute(
            "SELECT id, title FROM lessons WHERE user_id = (SELECT id FROM users WHERE username='charlie') ORDER BY id LIMIT 1"
        ).fetchone()
        lid = row["id"]
        title = (row["title"] or "").encode("utf-8")
    r = c.get(f"/lesson/{lid}")
    assert r.status_code == 200
    assert title in r.data


def test_wrong_user_lesson_redirects_not_500(app):
    c = app.test_client()
    login(c, "chris", "0822")
    with app.app_context():
        from app.db import get_db

        db = get_db()
        charlie_lid = db.execute(
            "SELECT id FROM lessons WHERE user_id = (SELECT id FROM users WHERE username='charlie') LIMIT 1"
        ).fetchone()["id"]
    r = c.get(f"/lesson/{charlie_lid}")
    assert r.status_code == 302
    assert "/games" in (r.headers.get("Location") or "")
