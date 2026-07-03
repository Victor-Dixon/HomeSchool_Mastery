# Product Requirements Document - HomeSchool Mastery

| Field | Value |
|---|---|
| Repo | Victor-Dixon/HomeSchool_Mastery |
| Product | HomeSchool Mastery |
| Canonical implementation | `lessons_lan/` |
| Status | Active documentation-synchronized Flask LAN app |
| Updated | 2026-07-03 |

## What this project is

HomeSchool Mastery is a local-first family homeschool learning platform. The
canonical app is `lessons_lan/`, a Flask/Jinja/SQLite LAN app for student
lessons, TEKS/STAAR-aligned practice, learning games, XP/mastery accountability,
boss fights, gear rewards, feedback, and parent/admin operations.

The repository also contains a root Node mastery prototype and an `ai_tutor/`
support package. Those contexts are present but are not the canonical product
unless explicitly referenced.

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
| Student | Seeded users include Charlie and Chris in `lessons_lan/app/db.py` | Complete lessons, practice, play learning games, earn XP/rewards, submit feedback |
| Parent/Admin | Seeded `admin` account in `lessons_lan/app/db.py` | Manage lessons/accounts, review feedback, operate local app |
| Operator | Same household maintainer role | Start/stop app, run tests, back up data, avoid destructive resets |

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
- Text Detective, Discount Dash, Fraction Battle, Story Duel, Spelling Lab, and
  Vocabulary Signal Breaker.
- Student feedback and admin feedback review.
- Optional local Ollama lesson coaching and Story Duel grading fallback.
- Tests under `lessons_lan/tests/`.

## Out of scope for the current canonical app

- Required cloud dependency.
- Multi-household or school deployment.
- OAuth, email, LMS integration, or hosted analytics.
- Treating the Node prototype or `ai_tutor/` JSON progress as shared canonical
  persistence for `lessons_lan/`.
- Destructive data cleanup during normal student/admin use.

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
| `data/progress.json` | `ai_tutor/` support package | Not canonical; per-Discord-user support progress |

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

## Remaining work

- Verify and document data backup/export for `lessons_lan`.
- Add CI for the current Python tests.
- Expand admin/mastery dashboard test coverage.
- Add TEKS coverage reporting and clarify full standards import status.
- Expand question/content variety with TEKS tags and item types.
- Decide whether the Node prototype remains legacy, gets archived, or is
  reintegrated; current operational status is Unknown.
- Decide whether `ai_tutor/` remains a support package or becomes integrated
  with the canonical app; current deployment status is Unknown.

## Success criteria

| Criterion | Verification |
|---|---|
| New contributor can identify the canonical app | README, AGENTS, this PRD, and docs index all point to `lessons_lan/` |
| Domain entities are mapped | `docs/DOMAIN_MODEL.md` includes entities, value objects, services, relationships, data flow, integrations, and feature mapping |
| Learner data is protected | Reset commands documented as operator-only; no student route exposes destructive reset |
| Behavior changes are test-backed | Targeted tests run from `lessons_lan/` before behavior changes |
| Documentation remains synchronized | Root summaries and expanded docs are updated together |

## Unknowns

- Complete TEKS corpus import and coverage.
- Active household use of the root Node prototype.
- Active household deployment of the `ai_tutor/` Discord bot.
- Cross-runtime data synchronization.
- Production backup/export path for canonical learner data.
