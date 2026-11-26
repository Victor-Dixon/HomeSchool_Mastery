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
- [x] Verify admin/student route boundaries and CLI-only destructive reset in isolated tests; PR #14, CI `45722603823`.
- [x] Resolve default session-signing key in source and isolated CI (PR #16, CI `45724342656`).
- [x] Secure first-run account provisioning in isolated CI (PR #17).
- [ ] Verify explicit rotation of existing legacy household credentials before live exposure.
- [ ] Verify Windows signing-key ACL and live deployment configuration.
- [x] Expand admin/mastery dashboard regression coverage (PRs #18 and #19).
- [ ] [DEFERRED] Add TEKS skill/question coverage reporting.
- [ ] Complete remaining `PRODUCTION_READINESS.md` checklist items.

### Portfolio / ownership hygiene

- [ ] Keep external family-pilot activation `READINESS_HELD` (readiness package PR #5 merged) until its documented readiness gates are independently satisfied or explicitly bounded out.
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

Use `NEXT_UP.md` for the immediate execution contract. Admin/mastery regression coverage is the next source readiness lane; live deployment remains held. Do not advance
external pilot activation or adaptive/cross-runtime expansion ahead of that
proof.

PR #17 merged `046cfaf64f124735513858cc8f2dff8d76a74a9c`; exact-head canonical CI `45738041920` passed. Secure first-run provisioning, atomic seeding and isolated preservation regressions integrated. Existing household credential rotation, Windows ACL, live deployment and external pilot authorization remain held; no production data modified.

## 2026-11-26 — Operator priority decision: maintenance-only

HomeSchool Mastery is dormant for feature delivery. The operator deprioritized the product because household learners returned to public school. Defer TEKS skill/question coverage reporting, curriculum enhancements, mastery expansion, prototype consolidation and external pilot activity until explicitly reactivated. Preserve source, existing accounts, hashes, learner records and backups; no live shutdown, data deletion, credential rotation or deployment is authorized by this decision. Retain Windows ACL, existing legacy credential rotation, deployment verification and external pilot authorization as unresolved security/operational obligations; address an actual security incident through authorized maintenance. Routine feature assignments are not eligible. Governed merged-branch retirement remains maintenance, not feature work.

Verified source checkpoint: PR #17 merged `046cfaf64f124735513858cc8f2dff8d76a74a9c` (CI `45738041920`), #18 merged `cfa745b89f95b8d9ab0ba230471d64a30aeb9c51` (CI `45738427687`), #19 merged `8c37081e5bdabb6236fa9253c754cb1d53830ab0` (CI `45739114459`). No production acceptance is claimed.
