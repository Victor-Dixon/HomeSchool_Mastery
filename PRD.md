# Product Requirements Document - Summary

> Canonical expanded PRD: `docs/PRD.md`
> Updated: 2026-08-16

## What is this project?

HomeSchool_Mastery is a local-first family homeschool learning platform. The
canonical app is `lessons_lan/`, a Flask/Jinja/SQLite LAN app for daily lessons,
practice, learning games, XP/mastery accountability, boss fights, gear rewards,
student feedback, and parent/admin workflows.

## Why does it exist?

It helps a household run simple, accountable homeschool sessions: students see
today's work and practice skills, while the parent/admin manages lessons,
accounts, feedback, and local operation.

## Domain

Family homeschool education and learner accountability, with TEKS/STAAR-aligned
Math and Reading/ELAR practice. Complete TEKS corpus coverage is Unknown.

## Current users

- Students: complete lessons, practice, games, boss fights, and feedback.
- Parent/Admin: manages lessons/accounts and reviews feedback.
- Operator: starts/stops the LAN app, runs tests, protects and backs up local data.

## Completed

- Canonical Flask LAN app identified under `lessons_lan/`.
- SQLite schema, seeded users/lessons/questions, routes, templates, and tests exist for the canonical app.
- Documentation synchronized around the current domain model on 2026-07-03.
- Canonical GitHub Actions `lessons_lan CI` established through PR #6 and independently verified at its exact head before merge.
- Existing test-runtime optimization salvaged from stale PR #4, reverified under current CI as PR #7, merged, and the old PR closed as superseded.

## Remaining

- Backup/export plus isolated restore/smoke verification for learner data.
- Expanded admin/mastery dashboard and route-boundary test coverage.
- Verification that destructive reset cannot be exposed to student flows.
- TEKS coverage reporting and full standards import clarity.
- Decision on whether the root Node prototype and `ai_tutor/` remain support contexts, are archived, or are integrated.

## Requirements

1. Serve a LAN-accessible Flask learning app from `lessons_lan/`.
2. Preserve learner safety and local-first operation.
3. Track lessons, completions, attempts, XP, levels, boss attempts, gear, and feedback in local persistence.
4. Keep parent/admin routes separated from student routes.
5. Back behavior changes with targeted tests and exact-head CI evidence for relevant pull requests.
6. Protect learner data with verified backup/restore operations before production-readiness claims.
7. Mark unverified architecture or requirements as Unknown.

## Non-goals

- Required cloud dependency.
- Destructive learner-data cleanup during normal use.
- Treating legacy/support runtimes as canonical without implementation evidence.
- Treating a draft family-pilot package as evidence of market validation, production readiness, or external adoption.
