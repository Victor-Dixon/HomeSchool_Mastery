# Project Structure Tree

> Updated: 2026-07-03

## What is this project?

HomeSchool_Mastery is a local-first family homeschool learning platform.

## Domain

Family homeschool education and learner accountability, with TEKS/STAAR-aligned
Math and Reading/ELAR practice.

## Structure

```text
HomeSchool_Mastery/
+-- README.md
+-- AGENTS.md
+-- PRD.md
+-- ROADMAP.md
+-- MASTER_TASK_LIST.md
+-- MASTER_TASK_LOG.md
+-- NEXT_UP.md
+-- PRODUCTION_READINESS.md
+-- PROJECT_STRUCTURE_TREE.md
+-- CONSOLIDATION_MANIFEST.md
+-- docs/
|   +-- README.md
|   +-- DOMAIN_MODEL.md
|   +-- PRD.md
|   +-- ROADMAP.md
|   +-- parity/
+-- runtime/
|   +-- tasks/
|       +-- master_task_list.md
|       +-- master_task_log.md
+-- lessons_lan/
|   +-- README.md
|   +-- PASSDOWN.md
|   +-- TASKLIST.md
|   +-- main.py
|   +-- run.py
|   +-- app/
|   +-- plugins/
|   +-- tests/
|   +-- requirements.txt
|   +-- requirements-dev.txt
+-- ai_tutor/
|   +-- README.md
|   +-- api.py
|   +-- bot.py
|   +-- tutor.py
|   +-- progress.py
|   +-- questions.py
|   +-- cogs/
+-- tests/
|   +-- quiz-engine.test.js
|   +-- test_ai_tutor_api.py
+-- server.js
+-- app.html
+-- quiz-engine.js
+-- ai_tutor_launcher.py
+-- requirements.txt
```

## Canonical source

`lessons_lan/` is the active canonical implementation.

## Present but non-canonical contexts

- Root Node prototype: `server.js`, `app.html`, `quiz-engine.js`.
- AI tutor support package: `ai_tutor/`.

Their future status is open: maintain separately, integrate with the canonical
app, or archive.
