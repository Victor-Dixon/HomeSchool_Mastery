# HomeSchool Mastery

Local-first family homeschool learning platform for TEKS/STAAR-aligned lessons,
practice games, XP/mastery accountability, and parent/admin oversight on a home
LAN.

## What this project is

HomeSchool Mastery is a family learning platform repository. The canonical app
is `lessons_lan/`, a Flask/Jinja/SQLite web app designed to run on a household
computer and serve students on the home network.

The canonical app provides:

- daily lessons and checklist completion
- TEKS/STAAR-aligned Math and Reading/ELAR practice
- learning games
- XP, levels, mastery gates, boss fights, and gear rewards
- student feedback and admin review
- parent/admin lesson and account management
- optional local Ollama AI coaching

The repository also contains a root Node prototype and an `ai_tutor/` support
package. They are present contexts, but `lessons_lan/` is the current
implementation source of truth.

## Why it exists

The project exists to make homeschool work visible, motivating, and accountable
without requiring cloud services. Students can see what to do next and receive
immediate practice feedback. A parent/admin can manage lessons, passwords, and
feedback from the same local system.

## Domain

Primary domain: family homeschool education and learner accountability.

Curriculum domain: TEKS/STAAR-aligned Math and Reading/ELAR practice. Complete
TEKS corpus import and full standards coverage are Unknown in the current repo;
the canonical app includes seeded standards, TEKS-tagged questions, and tests
for current behavior.

## Users

| User type | Current implementation |
|---|---|
| Students | Log in, view Today, open lessons, practice, play games, earn XP/rewards, submit feedback |
| Parent/Admin | Manage lessons, reset passwords, review feedback, operate the local app |
| Operator | Start/stop the LAN server, run tests, back up data, avoid destructive resets |

## Canonical architecture

```text
Browser/tablet on home LAN
        |
        v
lessons_lan/run.py or main.py
        |
        v
Flask app factory
        |
        +-- student routes: Today, lessons, practice, games, Adventure, feedback
        +-- admin routes: users, lessons, feedback inbox
        +-- game routes: Story Duel, Text Detective, Discount Dash, Spelling Lab
        +-- plugin hook: daily lesson generation
        |
        +-- SQLite: lessons_lan/instance/homeschool.db
        +-- Flask session and signed Story Duel tokens
        +-- JSON Story Duel bundles
        +-- optional local Ollama HTTP API
```

## Major domain entities

See `docs/DOMAIN_MODEL.md` for the complete model. Major canonical entities
include:

- User
- Lesson
- Completion
- Standard and LessonStandard
- Question and QuestionAttempt
- BossAttempt and Assessment
- PlayerState
- Gear and GearUnlock
- Badge and BadgeAward (schema exists; award behavior is Unknown)
- Feedback
- StoryDuelBundle and DuelState
- game session state stored in Flask session

## Feature-to-domain map

| Feature | Domain area |
|---|---|
| Today checklist | Lessons and completions |
| Practice and snake practice | Questions, attempts, XP |
| Adventure page | Player state, mastery gates, boss milestones |
| Boss fight | Questions, attempts, assessments, gear rewards |
| Text Detective / Discount Dash / Fraction Battle | Learning games and XP |
| Story Duel | JSON bundles, signed state, optional Ollama grading |
| Spelling Lab / Vocabulary Signal Breaker | Vocabulary and spelling practice |
| Feedback | Student feedback and admin review |
| Admin lesson/user management | Parent/admin operations |
| Lesson AI coach | Optional local Ollama integration |

## Repository structure

```text
.
+-- lessons_lan/              # Canonical Flask LAN app
|   +-- app/                  # Routes, services, templates, static assets
|   +-- plugins/              # Daily lesson plugin
|   +-- tests/                # Canonical pytest suite
|   +-- run.py
|   +-- main.py
|   +-- README.md
+-- docs/                     # Documentation index, PRD, roadmap, domain model
+-- runtime/tasks/            # Expanded task list and task log
+-- ai_tutor/                 # Support package: Flask API + Discord bot + Ollama
+-- tests/                    # Root tests for support/prototype contexts
+-- server.js                 # Root Node prototype runtime
+-- app.html                  # Root Node prototype UI
+-- quiz-engine.js            # Root Node prototype quiz generator
+-- AGENTS.md                 # Agent rules and canonical app guidance
+-- PRD.md                    # PRD summary
+-- ROADMAP.md                # Roadmap summary
+-- MASTER_TASK_LIST.md       # Task summary
+-- MASTER_TASK_LOG.md        # Task log summary
+-- NEXT_UP.md                # Current next work
+-- PRODUCTION_READINESS.md   # Household readiness checklist
```

## Quick start: canonical app

From the repository root:

```bash
cd lessons_lan
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python run.py
```

Open:

- `http://127.0.0.1:5000` on the host computer
- `http://<your-LAN-ip>:5000` from another device on the same network

Windows PowerShell instructions and autostart options are in
`lessons_lan/README.md`.

## Stop the canonical app

If running in a terminal, press `Ctrl+C`. If installed through the Windows
Startup-folder or Scheduled Task scripts, use the matching uninstall script in
`lessons_lan/autostart/` and then stop any running Python process that launched
`lessons_lan/run.py`.

## Data location and safety

The canonical app stores local data in:

```text
lessons_lan/instance/homeschool.db
```

Do not delete generated databases or student data as part of normal work.
`reset-db --yes` exists for operator-only maintenance and wipes local progress.
Back up the SQLite file before destructive maintenance.

## Verification

Canonical app tests:

```bash
cd lessons_lan
pytest -q
```

Root tests exist for support/prototype contexts:

- `tests/quiz-engine.test.js`
- `tests/test_ai_tutor_api.py`

## Current status

Completed:

- `lessons_lan/` identified as canonical.
- Documentation-first domain model audit completed on 2026-07-03.
- PRD, roadmap, task docs, NextUp, AGENTS, README, production readiness, and
  app-local docs synchronized around the canonical app.
- Current Flask app has tests for smoke routes, lessons, mastery, loot, boss
  rewards, generator behavior, item types, snake practice, and Story Duel.

Remaining:

- Run and preserve the canonical test gate.
- Add CI for current tests.
- Add backup/export verification for learner data.
- Add TEKS skill/question coverage report.
- Expand admin/mastery route tests.
- Decide whether the root Node prototype is maintained, integrated, or archived.
- Decide whether `ai_tutor/` remains a support package or integrates with
  `lessons_lan/`.

## Documentation map

- Documentation index: `docs/README.md`
- Product requirements: `docs/PRD.md`
- Domain model: `docs/DOMAIN_MODEL.md`
- Roadmap: `docs/ROADMAP.md`
- Task list/log: `runtime/tasks/master_task_list.md`,
  `runtime/tasks/master_task_log.md`
- Current next work: `NEXT_UP.md`
- Agent rules: `AGENTS.md`
- Canonical app operations: `lessons_lan/README.md`

## External integrations

- SQLite: required local persistence for `lessons_lan/`.
- Waitress: default WSGI server for `lessons_lan/run.py`.
- Ollama: optional local AI coach/grading integration.
- Discord: present only in the `ai_tutor/` support package.

No current docs or code prove a cloud database, OAuth, email delivery, hosted
analytics, or LMS integration.

## Recommended GitHub repository description

Use this repository description in GitHub settings:

> Local-first family homeschool learning platform for TEKS/STAAR-aligned lessons, practice games, XP/mastery accountability, and parent/admin oversight on a home LAN.
