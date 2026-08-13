# Next Up

> Updated: 2026-08-13

This is the immediate execution queue. Keep it to 3-5 active tasks. Do not place
completed evidence or long backlog inventory here; use `MASTER_TASK_LOG.md` and
`MASTER_TASK_LIST.md` for those.

## What is this project?

HomeSchool_Mastery is a local-first family homeschool learning platform. The
canonical app is `lessons_lan/`.

## Why does it exist?

It supports daily lessons, TEKS/STAAR-aligned practice, learning games,
XP/mastery accountability, feedback, and parent/admin workflows on a home LAN.

## Domain

Family homeschool education and learner accountability.

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

Broader backlog remains in `MASTER_TASK_LIST.md` and
`runtime/tasks/master_task_list.md`; promote items here only when they become
one of the next 3-5 execution tasks.
