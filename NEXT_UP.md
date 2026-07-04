# Next Up

> Updated: 2026-07-03

## What is this project?

HomeSchool_Mastery is a local-first family homeschool learning platform. The
canonical app is `lessons_lan/`.

## Why does it exist?

It supports daily lessons, TEKS/STAAR-aligned practice, learning games,
XP/mastery accountability, feedback, and parent/admin workflows on a home LAN.

## Domain

Family homeschool education and learner accountability.

## Recently completed

- Documentation-first domain model audit.
- README/PRD/roadmap/task docs/AGENTS synchronization around `lessons_lan/`.
- Startup, shutdown, and database location documented for the canonical app.

## 1. Run and preserve the canonical test gate

**AC:** `cd lessons_lan && pytest -q` passes in the current environment or any
failure is documented with the failing tests and cause.

## 2. Add data backup/export verification

**AC:** A documented command or test exports `lessons_lan` learner data, reads it
back, and verifies row count and important columns for users, lessons,
completions, attempts, player state, gear unlocks, and feedback.

## 3. Add CI workflow for `lessons_lan`

**AC:** `.github/workflows/ci.yml` runs the current Python test gate on push/PR
to `master`, and the workflow passes on the current suite.

## 4. Expand admin/mastery route tests

**AC:** Admin lesson/user/feedback routes and Adventure/mastery pages have
focused tests for authorized, unauthorized, and expected-content behavior.

## 5. Add TEKS skill/question coverage report

**AC:** A script reports coverage of tracked standards/TEKS tags by subject and
grade from the canonical SQLite/question-bank data, marking missing full-corpus
coverage as Unknown rather than assumed complete.

## 6. Finish production readiness checklist

**AC:** `PRODUCTION_READINESS.md` covers pre-deploy checks, backup/restore,
network configuration, startup/shutdown, smoke tests, rollback/reset boundaries,
and admin/student route separation.

## 7. Document canonical route/API surface

**AC:** A doc lists `lessons_lan` routes by actor (student/admin/operator/API),
required auth, request method, and domain entities touched.

## 8. Expand question/content variety

**AC:** New Reading and Math questions include TEKS tags, item types, tests where
behavior changes, and no weakened mastery/XP behavior.

## 9. Decide root Node prototype status

**AC:** A documented decision states whether the root Node runtime is maintained
separately, archived, or reintegrated, and updates docs/tests accordingly.

## 10. Decide `ai_tutor/` support-package status

**AC:** A documented decision states whether `ai_tutor/` remains separate support
tooling or becomes integrated with `lessons_lan`; if integrated, shared data
flow and tests are added.
