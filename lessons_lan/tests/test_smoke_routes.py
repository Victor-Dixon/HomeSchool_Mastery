"""
Smoke tests for routes added after the core suite (Spelling Lab, Vocabulary Breaker, run.py app).
Failing here usually means blueprint/import issues — run: pytest tests/test_smoke_routes.py -v
"""

from __future__ import annotations

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    import sqlite3

    db_path = tmp_path / "smoke.db"
    a = create_app()
    a.config.update(
        TESTING=True,
        SECRET_KEY="test",
        DATABASE=str(db_path),
    )
    with a.app_context():
        from app.db import init_db, seed_if_empty

        init_db()
        seed_if_empty()
        con = sqlite3.connect(str(db_path))
        assert con.execute("SELECT COUNT(*) FROM users").fetchone()[0] >= 1
        con.close()
    yield a


@pytest.fixture()
def client(app):
    return app.test_client()


def _login(client, username: str, password: str):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)


def test_run_module_exposes_flask_app():
    """Same import path as Waitress (python run.py)."""
    import run

    assert run.app is not None
    assert run.app.name == "app"


def test_url_map_includes_spelling_lab_and_vocab_signal(app):
    rules = {r.rule for r in app.url_map.iter_rules()}
    assert "/spelling-lab" in rules
    assert "/games/vocabulary-signal-breaker" in rules


def test_vocabulary_game_words_non_empty():
    from vocabulary_game import WORDS

    assert isinstance(WORDS, dict)
    assert len(WORDS) >= 1


def test_spelling_lab_core_loads():
    from spelling_lab_core import load_word_list

    w = load_word_list()
    assert len(w) >= 1


def test_spelling_lab_redirects_unauthenticated(client):
    r = client.get("/spelling-lab", follow_redirects=False)
    assert r.status_code == 302
    loc = r.headers.get("Location") or ""
    assert "login" in loc.lower()


def test_spelling_lab_renders_after_login(client):
    _login(client, "charlie", "34086028")
    r = client.get("/spelling-lab")
    assert r.status_code == 200, r.data[:500]
    assert b"Spelling Lab" in r.data


def test_vocab_signal_breaker_redirects_unauthenticated(client):
    r = client.get("/games/vocabulary-signal-breaker", follow_redirects=False)
    assert r.status_code == 302


def test_vocab_signal_breaker_renders_after_login(client):
    _login(client, "charlie", "34086028")
    r = client.get("/games/vocabulary-signal-breaker")
    assert r.status_code == 200, r.data[:500]
    assert b"Vocabulary" in r.data and b"Breaker" in r.data


def test_games_hub_renders_after_login(client):
    _login(client, "charlie", "34086028")
    r = client.get("/games")
    assert r.status_code == 200
    assert b"Spelling Lab" in r.data
    assert b"Vocabulary Signal Breaker" in r.data


def test_spelling_lab_api_start_returns_json_after_login(client):
    _login(client, "charlie", "34086028")
    r = client.post(
        "/api/spelling-lab/start",
        json={"mode": "scramble"},
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 200, r.data
    data = r.get_json()
    assert data.get("ok") is True
    assert data.get("total", 0) >= 1
