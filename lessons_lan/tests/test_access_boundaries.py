"""Exercise real Flask route guards against an isolated SQLite fixture."""
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from app import create_app
from app.db import get_db, init_db, seed_if_empty


@pytest.fixture
def boundary_app(tmp_path, monkeypatch):
    # The factory initializes the database before callers can update config.
    # Redirect Flask's instance path before factory execution.
    from flask import Flask
    original = Flask.__init__

    def isolated_init(self, *args, **kwargs):
        kwargs["instance_path"] = str(tmp_path / "instance")
        original(self, *args, **kwargs)

    monkeypatch.setattr(Flask, "__init__", isolated_init)
    app = create_app()
    app.config.update(TESTING=True, SECRET_KEY="isolated-test-key")
    with app.app_context():
        init_db()
        seed_if_empty()
        db = get_db()
        student = db.execute("SELECT id FROM users WHERE is_admin=0 ORDER BY id LIMIT 1").fetchone()[0]
        admin = db.execute("SELECT id FROM users WHERE is_admin=1 ORDER BY id LIMIT 1").fetchone()[0]
        lesson = db.execute("SELECT id FROM lessons WHERE user_id=? LIMIT 1", (student,)).fetchone()[0]
    return app, student, admin, lesson


def snapshot(app):
    with app.app_context():
        db = get_db()
        return {table: [tuple(row) for row in db.execute(f"SELECT * FROM {table} ORDER BY rowid")]
                for table in ("users", "lessons", "completions", "feedback", "player_state")}


def set_identity(client, user_id):
    with client.session_transaction() as session:
        session["user_id"] = user_id


@pytest.mark.parametrize("authenticated", [False, True])
def test_admin_routes_reject_non_admin_without_mutation(boundary_app, authenticated):
    app, student, admin, lesson = boundary_app
    client = app.test_client()
    if authenticated:
        set_identity(client, student)
    expected = "/today" if authenticated else "/login"
    before = snapshot(app)
    routes = [
        ("GET", "/admin", {}),
        ("GET", "/admin/feedback", {}),
        ("GET", f"/admin/users/{admin}", {}),
        ("POST", f"/admin/users/{admin}", {"new_password": "isolated-test-password"}),
        ("GET", "/admin/lessons", {}),
        ("POST", "/admin/lessons", {"action": "add", "user_id": student, "subject": "Math", "title": "Denied"}),
        ("GET", f"/admin/lessons/{lesson}/edit", {}),
        ("POST", f"/admin/lessons/{lesson}/edit", {"subject": "Math", "title": "Denied"}),
        ("POST", f"/admin/lessons/{lesson}/delete", {}),
    ]
    # Cover all registered admin HTTP methods, not only a hand-picked subset.
    expected_methods = {(rule.rule, method) for rule in app.url_map.iter_rules()
                        if rule.rule.startswith("/admin")
                        for method in rule.methods - {"HEAD", "OPTIONS"}}
    assert len(expected_methods) == len(routes)
    for method, path, data in routes:
        response = client.open(path, method=method, data=data)
        assert response.status_code == 302, (method, path)
        assert urlsplit(response.headers["Location"]).path == expected
    assert snapshot(app) == before


def test_reset_is_cli_only_and_student_cannot_reset(boundary_app):
    app, student, _, _ = boundary_app
    client = app.test_client()
    set_identity(client, student)
    before = snapshot(app)
    assert "reset-db" in app.cli.commands
    assert not any("reset-db" in rule.rule or "reset_db" in rule.endpoint
                   for rule in app.url_map.iter_rules())
    for path in ("/reset-db", "/admin/reset-db", "/reset_db"):
        for method in ("GET", "POST"):
            assert client.open(path, method=method).status_code == 404
    assert snapshot(app) == before


def test_admin_positive_control(boundary_app):
    app, student, admin, lesson = boundary_app
    client = app.test_client()
    set_identity(client, admin)
    for path in ("/admin", "/admin/feedback", "/admin/lessons", f"/admin/users/{student}",
                 f"/admin/lessons/{lesson}/edit"):
        assert client.get(path).status_code == 200, path
    response = client.post(f"/admin/lessons/{lesson}/edit",
                           data={"subject": "Math", "title": "Authorized fixture edit"})
    assert response.status_code == 302
    with app.app_context():
        assert get_db().execute("SELECT title FROM lessons WHERE id=?", (lesson,)).fetchone()[0] == "Authorized fixture edit"

def test_admin_password_rotation_preserves_other_accounts_and_learning(boundary_app):
    from werkzeug.security import check_password_hash
    app, student, admin, _ = boundary_app
    client = app.test_client()
    set_identity(client, admin)
    before = snapshot(app)
    response = client.post(f"/admin/users/{student}", data={"new_password": "tiny"})
    assert response.status_code == 200
    assert snapshot(app) == before
    password = "isolated-rotation-only-2026"
    response = client.post(f"/admin/users/{student}", data={"new_password": password})
    assert response.status_code == 302
    after = snapshot(app)
    with app.app_context():
        db = get_db()
        assert check_password_hash(db.execute("SELECT password_hash FROM users WHERE id=?", (student,)).fetchone()[0], password)
    assert [r for r in before["users"] if r[0] != student] == [r for r in after["users"] if r[0] != student]
    assert {k: v for k, v in before.items() if k != "users"} == {k: v for k, v in after.items() if k != "users"}


def test_admin_lesson_lifecycle_is_scoped(boundary_app):
    from datetime import date
    app, student, admin, lesson = boundary_app
    client = app.test_client()
    set_identity(client, admin)
    before = snapshot(app)
    payload = {"action": "add", "user_id": student, "date": date.today().isoformat(),
               "subject": "Math", "title": "", "sort_order": "99"}
    assert client.post("/admin/lessons", data=payload).status_code == 200
    assert snapshot(app) == before
    payload["title"] = "Isolated lifecycle fixture"
    assert client.post("/admin/lessons", data=payload).status_code == 302
    with app.app_context():
        db = get_db()
        created = db.execute("SELECT id FROM lessons WHERE title=? AND user_id=?", (payload["title"], student)).fetchone()[0]
    assert created != lesson
    assert client.post(f"/admin/lessons/{created}/edit", data={"subject": "Math", "title": "Updated fixture"}).status_code == 302
    with app.app_context():
        assert get_db().execute("SELECT title FROM lessons WHERE id=?", (created,)).fetchone()[0] == "Updated fixture"
    assert client.post(f"/admin/lessons/{created}/delete").status_code == 302
    assert snapshot(app) == before
