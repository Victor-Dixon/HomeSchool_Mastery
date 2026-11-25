"""Resolve a deployment signing key without logging or committing secret material."""
import os
import secrets
import tempfile
from pathlib import Path


def _validate(key):
    if len(key) < 32 or key.strip() != key or not key.strip() or len(set(key)) < 8:
        raise ValueError("Session signing key is invalid; configure a strong random key")
    return key


def resolve_signing_key(instance_path):
    configured = os.environ.get("HOMESCHOOL_SECRET_KEY")
    if configured is not None:
        return _validate(configured)
    directory = Path(instance_path)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "session-signing.key"
    # Publish a complete file atomically without overwriting another startup's key.
    if not path.exists():
        fd, temporary = tempfile.mkstemp(prefix=".session-signing-", dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(secrets.token_hex(32))
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(temporary, path)
            except FileExistsError:
                pass
        finally:
            os.unlink(temporary)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Session signing key must be a regular local file")
    if os.name == "posix" and path.stat().st_mode & 0o077:
        raise ValueError("Session signing key permissions must be owner-only")
    return _validate(path.read_text(encoding="utf-8"))
