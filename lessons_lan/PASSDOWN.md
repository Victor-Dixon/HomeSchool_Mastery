## Passdown (Homeschool Lessons / Dream.OS)

### Snapshot
- **App URL (LAN)**: `http://192.168.12.201:5000`
- **Passwords**:
  - **Charlie**: `34086028`
  - **Chris**: `0822`
- **Start**: `START.bat` (one click) or auto-start via `autostart/` Startup-folder script.
- **Tests**: `.\.venv\Scripts\python -m pytest` (currently green).

### What’s working
- **Today** list per student + **Open** lesson detail view.
- **Admin**: add lessons, delete lessons, **edit lesson details** (prevents “No details…” gap).
- **Feedback**: in-app feedback + admin inbox.
- **RPG**: XP/level tracking, Adventure page shows next boss.
- **Boss Fight V1**: TEKS-tagged question bank, grading, attempts persisted, assessments recorded, loot roll + gear unlocks.
- **Seed integrity**: seeded lessons always include required details; tests fail if not.

### Engineering notes (important)
- **Session IDs**: now UUID-backed to avoid collisions (`question_attempts.session_id`, `boss_attempts.session_id`).
- **Plugin loading**: `app/plugin_loader.py` registers modules into `sys.modules` to support import-time side effects (e.g., dataclasses).
- **DB**: SQLite in `instance/homeschool.db` (configurable via `app.config["DATABASE"]` for tests).

### Known gaps / next priorities
- **Content variety**: expand question bank (more Reading + Math, more TEKS tags, more item types).
- **Lesson engine**: make daily lessons generate practice sets and adapt based on recent misses (use `generator.py` + attempt history).
- **Mastery gates**: currently enforced mainly around milestone leveling; formalize tier map (1–100 with gates).
- **Ollama tutor NPC**: `app/tutor.py` exists; needs UI integration + skill-aware prompts.

### Standard operating procedure (SOP)
- **When adding a new feature**:
  - Add/extend tests in `tests/`.
  - Update `PASSDOWN.md` with what changed + what’s next.
  - Add tasks to the master task DB using `tools/master_tasks.py` (below).

