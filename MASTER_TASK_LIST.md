# Master Task List - Summary

> Expanded task list: `runtime/tasks/master_task_list.md`
> Updated: 2026-08-22

This file is the root summary backlog and strategic task inventory. It answers:
"What work exists in this repo?" Keep expanded backlog detail in
`runtime/tasks/master_task_list.md`.

## Planning file contract

| File | Purpose | Answers |
| --- | --- | --- |
| `MASTER_TASK_LIST.md` / `runtime/tasks/master_task_list.md` | Full backlog and strategic task inventory. | What work exists in this repo? |
| `MASTER_TASK_LOG.md` / `runtime/tasks/master_task_log.md` | Dated evidence, decisions, and completed work. | What happened, when, and why? |
| `NEXT_UP.md` | Immediate execution queue. | What should the next agent do right now? |

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

### Production readiness

- [ ] Maintain the canonical verification gate: `cd lessons_lan && python -m pytest -q`.
- [x] Add and verify learner-data backup/export plus isolated restore/smoke testing through PR #9; exact-head CI run `31946470759` succeeded before squash merge `8ed17074e860fb8b8dfc3e9ac4c2bd0401769987`.
- [ ] Verify admin/student route boundaries, including that destructive reset is unavailable to student flows.
- [ ] Expand admin/mastery dashboard tests where gaps remain.
- [ ] Add TEKS skill/question coverage reporting.
- [ ] Complete remaining `PRODUCTION_READINESS.md` checklist items.

### Portfolio / ownership hygiene

- [ ] Keep PR #5 (`docs/revenue: gate HomeSchool Mastery family pilot`) in `DRAFT / READINESS_HELD` until its documented readiness gates are independently satisfied or explicitly bounded out.
- [ ] Delete merged-stale/superseded branches only after current PR ownership and branch ancestry are revalidated immediately before deletion.

### Context decisions

- [ ] Decide status of root Node prototype: maintain separately, integrate, or archive.
- [ ] Decide status of `ai_tutor/`: support package or canonical integration.

## Done

- [x] Identify `lessons_lan/` as canonical implementation.
- [x] Confirm existing pytest coverage exists.
- [x] Add production readiness checklist file.
- [x] Document canonical app startup/shutdown/database location.
- [x] Audit stale README and architecture references.
- [x] Produce synchronized documentation-first domain model.
- [x] Update PRD, roadmap, task list, task log, NEXT_UP, AGENTS, README, and app docs around the current implementation.
- [x] Add the canonical `lessons_lan CI` workflow through PR #6 and verify its exact head successfully before merge.
- [x] Salvage PR #4's test-runtime optimization onto current master through PR #7, verify exact-head CI, merge the refreshed lane, and close PR #4 without merge as superseded.
- [x] Verify read-only learner-data backup, non-overwriting isolated restore, schema/row fidelity, and canonical-app readability through PR #9.

## Next operating step

Use `NEXT_UP.md` for the immediate execution contract. Admin/student route
boundary and destructive-reset isolation verification is the next readiness lane. Do not advance
external pilot activation or adaptive/cross-runtime expansion ahead of that
proof.
