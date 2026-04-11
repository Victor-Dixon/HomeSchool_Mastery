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

    with a.app_context():
        from app.db import init_db, seed_if_empty

        init_db()
        seed_if_empty()

    yield a


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, username, password):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)


def test_boss_victory_awards_gear_unlock(client, app):
    login(client, "chris", "0822")

    r = client.get("/boss/10")
    assert r.status_code == 200

    with app.app_context():
        from app.db import get_db

        db = get_db()
        qs = db.execute("SELECT id, answer_key FROM questions WHERE subject='Reading (ELAR)' ORDER BY id LIMIT 2").fetchall()
        assert len(qs) >= 1
        form = {f"q_{q['id']}": q["answer_key"] for q in qs}

    r2 = client.post("/boss/10", data=form, follow_redirects=True)
    assert r2.status_code == 200
    assert b"Boss Result" in r2.data

    with app.app_context():
        from app.db import get_db

        db = get_db()
        u = db.execute("SELECT id FROM users WHERE username='chris'").fetchone()
        count = db.execute("SELECT COUNT(*) AS c FROM gear_unlocks WHERE user_id = ?", (u["id"],)).fetchone()["c"]
        assert count >= 1

