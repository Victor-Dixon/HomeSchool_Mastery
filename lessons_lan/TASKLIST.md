# Tasklist - Homeschool Lessons LAN App

> Updated: 2026-07-03

## What is this app?

`lessons_lan/` is the canonical HomeSchool Mastery Flask LAN app for daily
lessons, practice, games, XP/mastery accountability, feedback, and parent/admin
operations.

## Domain

Family homeschool education and learner accountability, with TEKS/STAAR-aligned
Math and Reading/ELAR practice.

## Now

- [ ] Keep `pytest -q` passing from this folder.
- [ ] Add backup/export verification for learner data in `instance/homeschool.db`.
- [ ] Add CI for the current Python tests.
- [ ] Expand admin/mastery route tests.
- [ ] Add TEKS skill/question coverage report.
- [ ] Expand Reading and Math question bank with TEKS tags and item types.

## Next

- [ ] Decide whether `app/generator.py` should drive daily lesson practice sets
      from recent misses.
- [ ] Formalize mastery tier map for levels 1-100 and boss gates.
- [ ] Add route/API reference for student, admin, and game routes.
- [ ] Improve backup/restore and household production readiness docs after
      verification exists.

## Later

- [ ] Adaptive difficulty ramp based on recent answer history.
- [ ] STAAR simulation mode with timed sets and blueprint-like mix.
- [ ] Adventure story progression tied to boss clears and weak-skill wins.
- [ ] Additional reward rules only with tests for XP/mastery behavior.

## Completed

- [x] Lesson AI coach UI/API route exists with optional local Ollama fallback.
- [x] Boss Fight V1 records attempts, assessments, and loot/gear unlocks.
- [x] Feedback form and admin inbox exist.
- [x] Documentation-first domain model audit synchronized app docs.
