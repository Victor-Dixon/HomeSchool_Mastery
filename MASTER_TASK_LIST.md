# Master Task List - Summary

> Expanded task list: `runtime/tasks/master_task_list.md`
> Updated: 2026-08-16

This file is the root summary backlog and strategic task inventory. It answers:
"What work exists in this repo?" Keep expanded backlog detail in
`runtime/tasks/master_task_list.md`.

## Planning file contract

| File | Purpose | Answers |
| --- | --- | --- |
| `MASTER_TASK_LIST.md` / `runtime/tasks/master_task_list.md` | Full backlog and strategic task inventory. | What work exists in this repo? |
| `MASTER_TASK_LOG.md` / `runtime/tasks/master_task_log.md` | Dated evidence, decisions, and completed work. | What happened, when, and why? |
| `NEXT_UP.md` | Immediate execution queue, limited to 3-5 active tasks. | What should the next agent do right now? |

## What is this project?

HomeSchool_Mastery is a local-first family homeschool learning platform. The
canonical app is `lessons_lan/`.

## Why does it exist?

It supports daily homeschool lessons, practice, games, XP/mastery accountability,
student feedback, and parent/admin workflows on a home LAN.

## Domain

Family homeschool education and learner accountability, with TEKS/STAAR-aligned
Math and Reading/ELAR practice.

## Open

- [ ] Run and preserve the canonical verification gate:
      `cd lessons_lan && pytest -q`.
- [ ] Add data backup/export verification for `lessons_lan` learner data.
- [ ] Add CI workflow for the current Python tests. ACTIVE as
      `lessons_lan_ci_20260816`; exact-head workflow success is required.
- [ ] Expand admin/mastery dashboard tests.
- [ ] Add TEKS skill/question coverage report.
- [ ] Complete remaining `PRODUCTION_READINESS.md` checklist items.
- [ ] Decide status of root Node prototype: maintain, integrate, or archive.
- [ ] Decide status of `ai_tutor/`: support package or canonical integration.

## Done

- [x] Identify `lessons_lan/` as canonical implementation.
- [x] Confirm existing pytest coverage exists.
- [x] Add production readiness checklist file.
- [x] Document canonical app startup/shutdown/database location.
- [x] Audit stale README and architecture references.
- [x] Produce synchronized documentation-first domain model.
- [x] Update PRD, roadmap, task list, task log, NEXT_UP, AGENTS, README, and app
      docs around the current implementation.

## Next operating step

Use `NEXT_UP.md` for the current 3-5 item execution queue. Complete the active
CI gate, then advance backup/export verification before expanding adaptive
diagnostics.
