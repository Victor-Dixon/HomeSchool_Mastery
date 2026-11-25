import pytest

from app.session_signing import resolve_signing_key


def test_generated_key_persists_and_is_unique(tmp_path, monkeypatch):
    monkeypatch.delenv("HOMESCHOOL_SECRET_KEY", raising=False)
    first = resolve_signing_key(tmp_path / "first")
    assert len(first) >= 64
    assert resolve_signing_key(tmp_path / "first") == first
    assert resolve_signing_key(tmp_path / "second") != first


@pytest.mark.parametrize("value", ["", "dev-change-me", "short", " " * 64])
def test_unsafe_external_key_rejected(tmp_path, monkeypatch, value):
    monkeypatch.setenv("HOMESCHOOL_SECRET_KEY", value)
    with pytest.raises(ValueError):
        resolve_signing_key(tmp_path)


def test_external_key_preferred(tmp_path, monkeypatch):
    import secrets
    key = secrets.token_hex(32)
    monkeypatch.setenv("HOMESCHOOL_SECRET_KEY", key)
    assert resolve_signing_key(tmp_path) == key
    assert not (tmp_path / "session-signing.key").exists()


def test_invalid_persisted_key_fails_closed(tmp_path, monkeypatch):
    monkeypatch.delenv("HOMESCHOOL_SECRET_KEY", raising=False)
    path = tmp_path / "session-signing.key"
    path.write_text("dev-change-me", encoding="utf-8")
    with pytest.raises(ValueError):
        resolve_signing_key(tmp_path)
    assert path.read_text(encoding="utf-8") == "dev-change-me"


def test_app_session_survives_restart_and_rejects_old_default(tmp_path, monkeypatch):
    from flask import Flask
    from app import create_app
    from app.db import get_db

    monkeypatch.delenv("HOMESCHOOL_SECRET_KEY", raising=False)
    original = Flask.__init__

    def isolated_init(self, *args, **kwargs):
        kwargs["instance_path"] = str(tmp_path / "instance")
        original(self, *args, **kwargs)

    monkeypatch.setattr(Flask, "__init__", isolated_init)
    first = create_app()
    with first.app_context():
        admin = get_db().execute("SELECT id FROM users WHERE is_admin=1 LIMIT 1").fetchone()[0]
    client = first.test_client()
    with client.session_transaction() as session:
        session["user_id"] = admin
    cookie = client.get_cookie("session").value

    second = create_app()
    assert first.secret_key == second.secret_key
    restarted = second.test_client()
    restarted.set_cookie("session", cookie)
    assert restarted.get("/admin").status_code == 200

    # The legacy predictable default must not authenticate after the upgrade.
    legacy = Flask("legacy")
    legacy.secret_key = "dev-change-me"
    forged = legacy.session_interface.get_signing_serializer(legacy).dumps({"user_id": admin})
    restarted.set_cookie("session", forged)
    response = restarted.get("/admin")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_concurrent_startups_share_one_key(tmp_path, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    monkeypatch.delenv("HOMESCHOOL_SECRET_KEY", raising=False)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: resolve_signing_key(tmp_path), range(16)))
    assert len(set(results)) == 1
    assert not list(tmp_path.glob(".session-signing-*"))


def test_insecure_posix_permissions_rejected(tmp_path, monkeypatch):
    import os
    if os.name != "posix":
        pytest.skip("POSIX mode check only")
    monkeypatch.delenv("HOMESCHOOL_SECRET_KEY", raising=False)
    resolve_signing_key(tmp_path)
    (tmp_path / "session-signing.key").chmod(0o644)
    with pytest.raises(ValueError, match="owner-only"):
        resolve_signing_key(tmp_path)
