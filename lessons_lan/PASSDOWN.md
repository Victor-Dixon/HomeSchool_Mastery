# Passdown - Homeschool Lessons LAN App

> Updated: 2026-07-03

## Snapshot

- **Canonical app**: `lessons_lan/`
- **Domain**: local-first family homeschool education and learner accountability
- **Default URL**: `http://127.0.0.1:5000` on the host, or
  `http://<LAN-IP>:5000` from tablets on the same network
- **Start**: `python run.py`, `START.bat`, or autostart scripts
- **Stop**: `Ctrl+C` for terminal runs; uninstall autostart scripts before
  disabling startup-managed runs
- **Database**: `instance/homeschool.db`
- **Tests**: `pytest -q` from this folder

## What is working

- **Today** list per student and lesson detail pages.
- **Practice** with TEKS-tagged question bank, grading, attempts, and XP.
- **Learning games**: snake practice, Fraction Battle, Text Detective, Discount
  Dash, Story Duel, Spelling Lab, Vocabulary Signal Breaker.
- **Lesson AI coach**: UI/API route exists and uses optional local Ollama with
  offline fallback messaging.
- **Feedback**: student feedback form and admin inbox.
- **Admin**: add, edit, delete lessons; reset user passwords.
- **RPG**: XP/level tracking, Adventure page, mastery gates around boss
  milestones.
- **Boss Fight V1**: grading, attempts, assessments, loot roll, and gear unlocks.
- **Seed integrity**: seeded lessons include required details; tests cover this.

## Engineering notes

- **Session IDs**: UUID-backed for `question_attempts.session_id` and
  `boss_attempts.session_id`.
- **Plugin loading**: `app/plugin_loader.py` loads plugin manifests and supports
  import-time side effects.
- **DB**: SQLite in `instance/homeschool.db`; tests can override
  `app.config["DATABASE"]`.
- **Story Duel state**: signed token plus JSON bundles, not only Flask session.
- **Generator**: `app/generator.py` is tested but not the current routed daily
  lesson engine.

## Known gaps / next priorities

- **Verification**: keep `pytest -q` passing and add CI.
- **Backup/export**: add verification for learner data backup/export.
- **Content variety**: expand Reading and Math questions with TEKS tags and item
  types.
- **TEKS coverage**: report tracked tags/standards by subject and grade.
- **Admin/mastery tests**: expand route coverage for admin and mastery flows.
- **Mastery gates**: formalize level 1-100 tier map and gate rules.
- **Context decisions**: decide whether root Node prototype and `ai_tutor/`
  remain separate, are archived, or are integrated.

## Standard operating procedure

When adding a feature:

1. Derive behavior from code/docs; mark Unknowns instead of guessing.
2. Add or extend tests in `tests/` for behavior changes.
3. Preserve learner data and do not weaken XP/mastery/accountability logic.
4. Keep student routes and admin routes separated.
5. Update `PASSDOWN.md`, `TASKLIST.md`, and repository docs if status changes.
