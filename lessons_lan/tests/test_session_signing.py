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
