from __future__ import annotations

import sqlite3

from app import create_app
from app.backup import backup_database, database_manifest, restore_database
from app.db import get_db, init_db, seed_if_empty


def test_backup_and_isolated_restore_preserve_canonical_learner_data(tmp_path):
    source = tmp_path / "source.db"
    backup = tmp_path / "backups" / "learner-data.db"
    restored = tmp_path / "restored" / "homeschool.db"

    source_app = create_app()
    source_app.config.update(TESTING=True, SECRET_KEY="test", DATABASE=str(source))
    with source_app.app_context():
        init_db()
        seed_if_empty()
        db = get_db()
        user_id = db.execute("SELECT id FROM users ORDER BY id LIMIT 1").fetchone()[0]
        lesson_id = db.execute(
            "SELECT id FROM lessons WHERE user_id = ? ORDER BY id LIMIT 1", (user_id,)
        ).fetchone()[0]
        db.execute(
            "INSERT OR REPLACE INTO completions (lesson_id) VALUES (?)", (lesson_id,)
        )
        db.execute(
            "INSERT INTO feedback (user_id, rating, message) VALUES (?, ?, ?)",
            (user_id, 5, "backup proof"),
        )
        db.execute(
            "INSERT OR REPLACE INTO player_state (user_id, xp, level, title) "
            "VALUES (?, ?, ?, ?)",
            (user_id, 125, 2, "Backup Tester"),
        )
        db.commit()
        db.execute("PRAGMA wal_checkpoint(TRUNCATE)")

    source_manifest = database_manifest(source)
    backup_database(source, backup)
    assert database_manifest(backup) == source_manifest

    restore_database(backup, restored)
    restored_manifest = database_manifest(restored)
    assert restored_manifest == source_manifest

    for table in ("users", "lessons", "completions", "question_attempts", "player_state", "gear_unlocks", "feedback"):
        assert table in restored_manifest
        assert restored_manifest[table]["columns"]

    assert restored_manifest["feedback"]["row_count"] >= 1
    assert restored_manifest["player_state"]["row_count"] >= 1

    restored_app = create_app()
    restored_app.config.update(TESTING=True, SECRET_KEY="test", DATABASE=str(restored))
    with restored_app.app_context():
        db = get_db()
        assert isinstance(db, sqlite3.Connection)
        assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == source_manifest["users"]["row_count"]
        assert db.execute(
            "SELECT COUNT(*) FROM feedback WHERE message = ?", ("backup proof",)
        ).fetchone()[0] == 1


def test_backup_and_restore_refuse_to_overwrite_existing_files(tmp_path):
    source = tmp_path / "source.db"
    target = tmp_path / "existing.db"
    sqlite3.connect(source).close()
    target.write_bytes(b"do not overwrite")

    try:
        backup_database(source, target)
    except FileExistsError:
        pass
    else:
        raise AssertionError("backup_database must refuse an existing destination")

    try:
        restore_database(source, target)
    except FileExistsError:
        pass
    else:
        raise AssertionError("restore_database must refuse an existing destination")

    assert target.read_bytes() == b"do not overwrite"
