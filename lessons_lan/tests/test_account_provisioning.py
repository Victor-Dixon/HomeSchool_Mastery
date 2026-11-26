"""Regression gates for first-run provisioning and household preservation."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from flask import Flask
from werkzeug.security import check_password_hash

from app.db import get_db, init_app, init_db, seed_if_empty


NAMES = ("ADMIN", "CHARLIE", "CHRIS")


def isolated_app(tmp_path):
    app = Flask(__name__, instance_path=str(tmp_path))
    app.config["DATABASE"] = str(tmp_path / "household.db")
    app.teardown_appcontext(__import__("app.db", fromlist=["close_db"]).close_db)
    with app.app_context():
        init_db()
    return app


def snapshot(db):
    return {table: [tuple(row) for row in db.execute(f"SELECT * FROM {table} ORDER BY rowid")]
            for table in ("users", "lessons", "completions", "player_state", "feedback")}


@pytest.mark.parametrize("mode", ["missing", "short", "duplicate"])
def test_invalid_bootstrap_leaves_database_empty(tmp_path, monkeypatch, mode):
    app = isolated_app(tmp_path)
    key = "HOMESCHOOL_BOOTSTRAP_ADMIN_PASSWORD"
    if mode == "missing":
        monkeypatch.delenv(key)
    elif mode == "short":
        monkeypatch.setenv(key, "short")
    else:
        monkeypatch.setenv(key, "isolated-fixture-charlie-only")
    with app.app_context():
        with pytest.raises(RuntimeError, match="First-run provisioning"):
            seed_if_empty()
        assert get_db().execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
        assert get_db().execute("SELECT COUNT(*) FROM lessons").fetchone()[0] == 0


def test_seed_hashes_and_restart_preserves_existing_household(tmp_path, monkeypatch):
    app = isolated_app(tmp_path)
    with app.app_context():
        seed_if_empty()
        db = get_db()
        rows = db.execute("SELECT * FROM users ORDER BY id").fetchall()
        assert len(rows) == 3
        for row in rows:
            assert check_password_hash(row["password_hash"], "isolated-fixture-" + row["username"] + "-only")
        learner = rows[1]["id"]
        db.execute("INSERT INTO player_state (user_id, xp, level, title) VALUES (?, 90, 2, 'Fixture')", (learner,))
        lesson = db.execute("SELECT id FROM lessons WHERE user_id=? LIMIT 1", (learner,)).fetchone()[0]
        db.execute("INSERT INTO completions (lesson_id) VALUES (?)", (lesson,))
        db.commit()
        before = snapshot(db)
    for name in NAMES:
        monkeypatch.delenv("HOMESCHOOL_BOOTSTRAP_" + name + "_PASSWORD")
    reopened = isolated_app(tmp_path)
    with reopened.app_context():
        seed_if_empty()
        assert snapshot(get_db()) == before


def test_concurrent_seed_is_atomic(tmp_path):
    app = isolated_app(tmp_path)
    barrier = Barrier(4)
    def worker(_):
        with app.app_context():
            barrier.wait(timeout=10)
            seed_if_empty()
            return snapshot(get_db())
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(worker, range(4)))
    assert all(result == results[0] for result in results)
    assert len(results[0]["users"]) == 3
    assert len(results[0]["lessons"]) == 5


def test_seed_rolls_back_if_lesson_insert_fails(tmp_path):
    app = isolated_app(tmp_path)
    with app.app_context():
        db = get_db()
        db.execute("CREATE TRIGGER reject_seed BEFORE INSERT ON lessons BEGIN SELECT RAISE(ABORT, 'fixture failure'); END")
        db.commit()
        with pytest.raises(Exception, match="fixture failure"):
            seed_if_empty()
        assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
        db.execute("DROP TRIGGER reject_seed")
        db.commit()
        seed_if_empty()
        assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 3
