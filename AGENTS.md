# AGENTS.md

## Role

HomeSchool_Mastery is the family homeschool learning platform repo.

Agents working here must preserve:

- learner safety
- local-first operation
- TEKS/STAAR alignment
- test-backed changes
- simple parent/operator workflows
- documentation synchronized with implementation

## Canonical App

The current canonical app lives under:

```text
lessons_lan/
```

Treat `lessons_lan/` and its tests as the current implementation signal. The
root Node app (`server.js`, `app.html`, `quiz-engine.js`) and `ai_tutor/`
package are present, but they are not the canonical app unless a future
test-backed change explicitly integrates them.

## Domain

Primary domain: family homeschool education and learner accountability.

Canonical app domain model:

- students and parent/admin users
- daily lessons and completions
- TEKS/STAAR-aligned Math and Reading/ELAR questions
- question attempts, boss attempts, assessments, XP, levels, mastery gates
- learning games, boss fights, loot/gear, feedback
- local SQLite persistence and optional local Ollama coaching

If a domain fact cannot be derived from code or docs, mark it as `Unknown`
instead of guessing.

## Documentation source of truth

- Documentation index: `docs/README.md`
- Product requirements: `docs/PRD.md` plus root `PRD.md` summary
- Domain model: `docs/DOMAIN_MODEL.md`
- Roadmap: `docs/ROADMAP.md` plus root `ROADMAP.md` summary
- Task list/log: `runtime/tasks/master_task_list.md`,
  `runtime/tasks/master_task_log.md`, plus root summaries
- Current next work: `NEXT_UP.md`
- Canonical app operations: `lessons_lan/README.md` and
  `lessons_lan/PASSDOWN.md`

Planning files have distinct roles:

- `MASTER_TASK_LIST.md` and `runtime/tasks/master_task_list.md` are backlog and
  strategic inventory: what work exists in this repo.
- `MASTER_TASK_LOG.md` and `runtime/tasks/master_task_log.md` are dated
  verified evidence/history: what closed, when, and why.
- `NEXT_UP.md` is the immediate 3-5 item execution queue: what the next agent
  should do right now.

When changing architecture, behavior, or project status, update the related docs
in the same change.

## Rules

- Do not delete student data or generated databases.
- Treat reset commands as operator-only maintenance; never expose destructive
  reset behavior to students.
- Do not weaken mastery, XP, boss, gear, attempts, accountability, or route
  separation logic without tests.
- Prefer small Flask/test changes in `lessons_lan/`.
- Run targeted tests for behavior changes.
- Keep parent/admin routes separated from student routes.
- Keep documentation internally consistent; remove stale Node-era assumptions
  when they conflict with the canonical Flask app.

## Standard Repository Working Contract

1. Read `AGENTS.md`, `NEXT_UP.md`, `MASTER_TASK_LIST.md`, `MASTER_TASK_LOG.md`, any repo SSOT/state manifest, branch/HEAD, and relevant tests before editing.
2. Work one bounded lane with explicit **TARGET, ACTION, VERIFY, COMMIT**. Do not mix unrelated cleanup, features, migrations, or speculative rewrites.
3. Use Fast TDD: smallest acceptance test, smallest safe change, targeted verification, then broad verification.
4. When repo state changes, update `NEXT_UP.md` and `MASTER_TASK_LIST.md` in the same lane, plus the execution-state SSOT when present.
5. Append the canonical task log only after verification proves closure. Never record planned or merely implemented work as completed.
6. For non-trivial work, create/update `runtime/tasks/*.yaml` with objective, scope, acceptance, verification, holds, and next lane when supported.
7. Trust but verify: targeted tests, repo validators, `git diff --check`, and final status/diff review. PASS/COMPLETE/deployed/merged claims require evidence.
8. Salvage before destructive cleanup. Classify variants/donor material before delete/reset/rewrite; preserve canonical source unless evidence proves it stale.
9. End code or repo-structure work with a clean scoped commit. Planning-only work still requires synchronized task surfaces and verification.
10. Leave the next executable step in `NEXT_UP.md` with its verification gate so the next agent does not rediscover the lane.

### Canonical Planning Names

Fleet-standard root planning names are `NEXT_UP.md`, `MASTER_TASK_LIST.md`, and `MASTER_TASK_LOG.md`. Existing explicit repo SSOTs remain authoritative until deliberately migrated; compatibility mirrors must not become competing authorities.
