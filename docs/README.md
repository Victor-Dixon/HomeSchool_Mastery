# Documentation Index - HomeSchool Mastery

> Last updated: 2026-07-03

This index is the documentation entrypoint for the repository.

## Project summary

HomeSchool Mastery is a local-first family homeschool learning platform. The
canonical implementation is the Flask LAN app in `lessons_lan/`, which provides
daily lessons, practice, learning games, XP/mastery accountability, boss fights,
gear rewards, feedback, and parent/admin workflows for a home network.

## Domain

The project models family homeschool education and learner accountability, with
TEKS/STAAR-aligned Math and Reading/ELAR practice. Complete TEKS corpus import,
full standards coverage, and cross-runtime data synchronization are Unknown in
the current repository unless a later implementation proves otherwise.

## Authoritative docs

| Question | Primary document | Supporting documents |
|---|---|---|
| What is the product and why does it exist? | `docs/PRD.md` | `PRD.md`, `README.md` |
| What domain does it model? | `docs/DOMAIN_MODEL.md` | `docs/PRD.md` |
| What entities and relationships exist? | `docs/DOMAIN_MODEL.md` | `lessons_lan/app/db.py` |
| What has been completed and what remains? | `runtime/tasks/master_task_log.md`, `runtime/tasks/master_task_list.md` | `MASTER_TASK_LOG.md`, `MASTER_TASK_LIST.md`, `NEXT_UP.md` |
| What should be worked on next? | `NEXT_UP.md` | `docs/ROADMAP.md`, `runtime/tasks/master_task_list.md` |
| How do agents work safely in this repo? | `AGENTS.md` | `CONSOLIDATION_MANIFEST.md` |
| How is the canonical app operated? | `lessons_lan/README.md` | `lessons_lan/PASSDOWN.md`, `PRODUCTION_READINESS.md` |

## Documentation hierarchy

The root `PRD.md`, `ROADMAP.md`, `MASTER_TASK_LIST.md`, and
`MASTER_TASK_LOG.md` are concise summaries for quick orientation. The expanded
canonical sources live in `docs/` and `runtime/tasks/`.

Do not update one copy without updating the corresponding canonical document:

- `PRD.md` and `docs/PRD.md`
- `ROADMAP.md` and `docs/ROADMAP.md`
- `MASTER_TASK_LIST.md`, `NEXT_UP.md`, and `runtime/tasks/master_task_list.md`
- `MASTER_TASK_LOG.md` and `runtime/tasks/master_task_log.md`
- `AGENTS.md`, `README.md`, and `CONSOLIDATION_MANIFEST.md` when the canonical
  app or architecture status changes

## Current implementation boundaries

| Runtime/context | Status in docs |
|---|---|
| `lessons_lan/` Flask app | Canonical product |
| Root Node app (`server.js`, `app.html`, `quiz-engine.js`) | Present but not canonical |
| `ai_tutor/` Flask/Discord package | Present support package, separate from canonical app |

When behavior differs between contexts, document the context explicitly.

## Recommended GitHub repository description

The current GitHub repository description should be:

> Local-first family homeschool learning platform for TEKS/STAAR-aligned lessons, practice games, XP/mastery accountability, and parent/admin oversight on a home LAN.

If the GitHub metadata cannot be edited from the current environment, keep this
description synchronized here and in the README until a maintainer updates the
repository settings.
