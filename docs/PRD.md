# Product Requirements Document - HomeSchool Mastery

| Field | Value |
|---|---|
| Repo | Victor-Dixon/HomeSchool_Mastery |
| Product | HomeSchool Mastery |
| Canonical implementation | `lessons_lan/` |
| Status | Active local-first Flask LAN app with canonical CI; production readiness still gated |
| Updated | 2026-08-16 |

## What this project is

HomeSchool Mastery is a local-first family homeschool learning platform. The
canonical app is `lessons_lan/`, a Flask/Jinja/SQLite LAN app for student
lessons, TEKS/STAAR-aligned practice, learning games, XP/mastery accountability,
boss fights, gear rewards, feedback, and parent/admin operations.

The repository also contains a root Node mastery prototype and an `ai_tutor/`
support package. Those contexts are present but are not the canonical product
unless explicitly integrated by test-backed work.

## Why it exists

The project exists to support a household learning workflow where students can:

- See today's assigned work.
- Practice Math and Reading/ELAR skills.
- Receive immediate feedback through XP, levels, games, and boss gates.
- Submit feedback to the parent/admin.

It also gives the parent/admin simple local workflows for lesson management,
password resets, feedback review, and operation of the home LAN app.

## Domain modeled

Primary domain: family homeschool education and learner accountability.

Curriculum domain: TEKS/STAAR-aligned Math and Reading/ELAR practice. Complete
TEKS corpus coverage is Unknown in the current implementation; the app contains
seeded standards and TEKS-tagged questions.

## Users

| User type | Current evidence | Needs |
|---|---|---|
| Student | Seeded student users in `lessons_lan/app/db.py` | Complete lessons, practice, play learning games, earn XP/rewards, submit feedback |
| Parent/Admin | Seeded admin account in `lessons_lan/app/db.py` | Manage lessons/accounts, review feedback, operate local app |
| Operator | Household maintainer role | Start/stop app, run tests, back up and restore data safely, avoid destructive resets |

## Problems solved

| Problem | Current solution |
|---|---|
| Daily work is hard to see and track | Today checklist and completion records |
| Practice needs accountability | Question attempts, XP, Adventure page, mastery gates |
| Students need motivation | Games, boss fights, gear unlocks, levels |
| Parent/admin needs simple control | Admin lesson CRUD, password reset, feedback inbox |
| Household wants local operation | SQLite + LAN server; no required cloud service |

## In scope

- LAN-accessible Flask app in `lessons_lan/`.
- Login/session-based student and admin views.
- Daily lessons and completion tracking.
- Practice quizzes and snake practice using the question bank.
- TEKS-tagged Math and Reading/ELAR questions.
- XP/level state and milestone mastery gates.
- Adventure page, boss fights, boss attempts, assessments, loot, and gear.
- Learning-game surfaces already present in the canonical app.
- Student feedback and admin feedback review.
- Optional local Ollama lesson coaching and Story Duel grading fallback.
- Tests under `lessons_lan/tests/`.
- Canonical GitHub Actions verification for relevant `lessons_lan` changes.

## Out of scope for the current canonical app

- Required cloud dependency.
- Multi-household or school deployment.
- OAuth, email, LMS integration, or hosted analytics.
- Treating the Node prototype or `ai_tutor/` JSON progress as shared canonical persistence for `lessons_lan/`.
- Destructive data cleanup during normal student/admin use.
- Treating the draft PR #5 family-pilot package as proof of market validation, customers, production readiness, or educational efficacy.

## Current architecture

```text
Browser/tablet on home LAN
        |
        v
lessons_lan/run.py or main.py
        |
        v
Flask app factory (app/__init__.py)
        |
        +-- routes blueprint: lessons, practice, games, boss, admin, feedback
        +-- spelling_lab blueprint
        +-- vocab_signal blueprint
        +-- plugins/teks_daily_training hook
        |
        +-- SQLite instance/homeschool.db
        +-- Flask session / signed Story Duel tokens
        +-- JSON Story Duel bundles
        +-- optional local Ollama HTTP API
```

## Data and persistence

| Store | Scope | Notes |
|---|---|---|
| `lessons_lan/instance/homeschool.db` | Canonical app SQLite DB | Users, lessons, completions, questions, attempts, boss attempts, assessments, player state, gear, feedback |
| Flask session | Canonical app runtime state | Login, game state, AI chat history, one-time XP guards |
| Story Duel JSON bundles | Canonical app content | Swappable battle/story content |
| Root `data.json` | Node prototype | Not canonical; generated if Node app runs |
| `data/progress.json` | `ai_tutor/` support package | Not canonical; support-package progress |

## Completed capabilities

- `lessons_lan/` is identified as the canonical implementation.
- Flask app factory, routes, templates, SQLite schema, seed data, and tests exist.
- Student Today, lesson detail, completion, practice, games, Adventure, boss,
  loot, feedback, and admin routes exist.
- Optional local Ollama hooks exist for lesson AI coach and Story Duel grading.
- Existing pytest coverage covers smoke routes, lesson pages, mastery, loot,
  boss rewards, item types, generator behavior, snake practice, Story Duel, and
  broader app flows.
- Documentation was synchronized around the canonical domain model on 2026-07-03.
- PR #6 established `lessons_lan CI`; exact-head run `31931001139` succeeded before merge.
- PR #7 revalidated and merged the test-runtime optimization on current master; exact-head run `31934385959` succeeded, and old PR #4 was closed as superseded.

- Learner-data backup/export and isolated restore/smoke: Verified through PR #9, exact-head CI `31946470759`, merge `8ed17074e860fb8b8dfc3e9ac4c2bd0401769987` (isolated test databases; not a live household restore).

- Access-boundary verification: PR #14 merged `59de341d38b73b292acc7fec4dc9f91e16ebb07f`; exact-head `lessons_lan CI` run `45722603823` succeeded. Isolated Flask/SQLite regression coverage: anonymous/student admin request denial, unchanged records, CLI-only reset, positive admin edit. This does not establish production security; live deployment remains held.

- Signing-key source acceptance: PR #16 merged `3bdcb4657c72dd36ae174ddafc34ef5aa69298e6`; exact-head CI `45724342656` passed. Isolated regression tests cover persistent random signing keys, invalid configuration rejection, restart session continuity, legacy cookie rejection, concurrent startup and POSIX permissions. Windows ACL and live deployment remain unverified; seeded account password security and external pilot remain held.

## Remaining work

- Assess seeded-account security and verify Windows ACL/live configuration before production readiness.
- Expand admin/mastery dashboard test coverage where gaps remain.
- Add TEKS coverage reporting and clarify full standards import status.
- Expand question/content variety with TEKS tags and item types.
- Decide whether the Node prototype remains legacy, gets archived, or is reintegrated; current operational status is Unknown.
- Decide whether `ai_tutor/` remains a support package or becomes integrated with the canonical app; current deployment status is Unknown.

## Success criteria

| Criterion | Verification |
|---|---|
| New contributor can identify the canonical app | README, AGENTS, this PRD, and docs index all point to `lessons_lan/` |
| Domain entities are mapped | `docs/DOMAIN_MODEL.md` includes entities, value objects, services, relationships, data flow, integrations, and feature mapping |
| Learner data is protected | Reset commands are operator-only; backup/export and isolated restore are verified before readiness claims |
| Behavior changes are test-backed | Targeted tests plus exact-head CI for relevant pull requests |
| Documentation remains synchronized | Root summaries and expanded docs are updated together |

## Unknowns

- Complete TEKS corpus import and coverage.
- Active household use of the root Node prototype.
- Active household deployment of the `ai_tutor/` support package.
- Cross-runtime data synchronization.
- Live household database restore, sustained operation, and broader production readiness are not established by isolated backup/restore acceptance.
