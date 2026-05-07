# AGENTS.md

## Role

HomeSchool_Mastery is the family learning platform repo.

Agents working here must preserve:
- learner safety
- local-first operation
- TEKS/STAAR alignment
- test-backed changes
- simple parent/operator workflows

## Canonical App

Current canonical app lives under:

lessons_lan/

Root README may contain older Node-era architecture notes. Treat lessons_lan/ and its tests as the current implementation signal.

## Rules

- Do not delete student data or generated databases.
- Do not weaken mastery/XP/accountability logic without tests.
- Prefer small Flask/test changes.
- Run targeted tests before commit.
- Keep parent/admin routes separated from student routes.
