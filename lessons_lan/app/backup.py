"""Safe backup and isolated restore helpers for the canonical learner database."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from urllib.parse import quote


def _read_only_connection(path: Path) -> sqlite3.Connection:
    resolved = path.resolve()
    uri_path = quote(str(resolved), safe="/:\\")
    return sqlite3.connect(f"file:{uri_path}?mode=ro", uri=True)


def _assert_integrity(connection: sqlite3.Connection) -> None:
    result = connection.execute("PRAGMA integrity_check").fetchone()
    if result is None or result[0] != "ok":
        raise RuntimeError(f"SQLite integrity check failed: {result!r}")


def backup_database(source_path: str | Path, backup_path: str | Path) -> Path:
    """Create a consistent SQLite backup without modifying the source database."""
    source = Path(source_path)
    destination = Path(backup_path)

    if not source.is_file():
        raise FileNotFoundError(source)
    if source.resolve() == destination.resolve():
        raise ValueError("backup destination must differ from source database")
    if destination.exists():
        raise FileExistsError(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)
    with _read_only_connection(source) as src, sqlite3.connect(destination) as dst:
        src.backup(dst)
        _assert_integrity(dst)

    return destination


def restore_database(backup_path: str | Path, restore_path: str | Path) -> Path:
    """Restore a backup into a new isolated database path; never overwrite a target."""
    backup = Path(backup_path)
    destination = Path(restore_path)

    if not backup.is_file():
        raise FileNotFoundError(backup)
    if backup.resolve() == destination.resolve():
        raise ValueError("restore destination must differ from backup database")
    if destination.exists():
        raise FileExistsError(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)
    with _read_only_connection(backup) as src, sqlite3.connect(destination) as dst:
        src.backup(dst)
        _assert_integrity(dst)

    return destination


def database_manifest(path: str | Path) -> dict[str, dict[str, object]]:
    """Return table row counts and column names for backup/restore verification."""
    db_path = Path(path)
    if not db_path.is_file():
        raise FileNotFoundError(db_path)

    manifest: dict[str, dict[str, object]] = {}
    with _read_only_connection(db_path) as connection:
        _assert_integrity(connection)
        table_rows = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        for (table_name,) in table_rows:
            quoted_name = '"' + table_name.replace('"', '""') + '"'
            row_count = connection.execute(f"SELECT COUNT(*) FROM {quoted_name}").fetchone()[0]
            columns = [
                row[1]
                for row in connection.execute(f"PRAGMA table_info({quoted_name})").fetchall()
            ]
            manifest[table_name] = {"row_count": row_count, "columns": columns}

    return manifest
