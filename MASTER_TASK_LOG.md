# Master Task Log - Summary

> Expanded task log: `runtime/tasks/master_task_log.md`
> Updated: 2026-08-22

This dated summary records completed work, decisions, blockers, and verification
evidence. It answers: "What happened, when, and why?" Keep expanded history in
`runtime/tasks/master_task_log.md`.

## What is this project?

HomeSchool_Mastery is a local-first family homeschool learning platform. The
canonical app is `lessons_lan/`.

## Why does it exist?

It supports daily lessons, practice, games, XP/mastery accountability, feedback,
and parent/admin operation on a home LAN.

## Domain

Family homeschool education and learner accountability, with TEKS/STAAR-aligned
Math and Reading/ELAR practice.

## Completed history

### 2026-05-07

- Added governance baseline artifacts.
- Classified `lessons_lan/` as canonical implementation.
- Preserved existing tests as verification gate.

### 2026-07-03

- Completed documentation-first domain model audit.
- Reconciled stale Node-era/multi-app architecture language with the canonical
  `lessons_lan/` implementation.
- Updated PRD, roadmap, master task list, task log, NEXT_UP, AGENTS, README,
  docs index, domain model, production readiness docs, and app-local docs.
- Marked Node prototype and `ai_tutor/` as present but non-canonical contexts.
- Recorded Unknowns instead of treating unverified architecture as shipped.

### 2026-08-13

- Reconciled the stranded local planning-standardization intent from `d4d18e7`
  onto remote `origin/master` after PR #2's documentation/domain-model work.
- Preserved remote PR #2 canonical `lessons_lan/` documentation and avoided
  duplicating planning sections.
- Standardized planning-file roles: task list for backlog, task log for dated
  evidence/history, and `NEXT_UP.md` for the immediate execution queue.
- Trimmed `NEXT_UP.md` to active execution items only; broader backlog remains
  in `MASTER_TASK_LIST.md` and `runtime/tasks/master_task_list.md`.

### 2026-08-16 - Canonical CI closure

- PR #6 (`ci: add lessons_lan canonical verification gate`) exact head:
  `997e4dd4402357a7d9c08d26c237be4201aa963b`.
- GitHub Actions `lessons_lan CI` run `31931001139` completed successfully at
  that exact head.
- PR #6 was squash-merged as
  `bad04a1d6e643663f248982678c13e40c8c93e89`.
- The new workflow runs the canonical `python -m pytest -q` gate from
  `lessons_lan/` for relevant pull-request and master changes.
- This closes the repository task to add a canonical CI gate; backup/export and
  other production-readiness work remain open.

### 2026-08-16 - PR #4 salvage / refresh

- Original PR #4 remained a unique two-file test/config optimization but was
  based on the pre-CI master and had no current exact-head CI evidence.
- Its unique intent was ported onto current master without wholesale-merging the
  stale branch as PR #7 (`test: refresh HomeSchool Mastery runtime reduction on current master`).
- PR #7 exact head: `681d86adc273f4fff0410445ee7eb0417a6c311b`.
- Exact-head `lessons_lan CI` run `31934385959` completed successfully.
- PR #7 was squash-merged as
  `89c7c6e1cf4b908f111fa627e11577f3930e2fcf`.
- Original PR #4 was then closed without merge as superseded; its conversation
  records PR #7 as the replacement, so no unique test work was discarded.

### 2026-08-16 - Post-salvage branch / PR audit

Audit-time comparisons against canonical master
`89c7c6e1cf4b908f111fa627e11577f3930e2fcf`:

- `docs/family-pilot-readiness-20260816`: 1 commit ahead / 2 behind; PR #5 remains
  `ACTIVE_PR / DRAFT / READINESS_HELD`. Its unique diff is the one-file bounded
  family-pilot readiness document.
- `docs/planning-reconciliation-20260813`: 0 ahead / 4 behind;
  `MERGED_STALE`.
- `feat/lessons-lan-ci-20260816`: raw ancestry 1 ahead / 2 behind after squash
  merge; classified `MERGED_STALE_BY_PR_6`, not salvage work.
- `test/app-runtime-reduction-20260813`: raw ancestry 1 ahead / 3 behind, but its
  file-level value was ported and merged through PR #7; classified
  `SUPERSEDED_BY_PR_7`.
- `test/app-runtime-reduction-refresh-20260816`: raw ancestry 2 ahead / 1 behind
  after squash merge; classified `MERGED_STALE_BY_PR_7`.
- No branch was deleted in this audit. Final branch deletion still requires
  immediate ownership/ancestry revalidation and a branch-deletion-capable path.

### 2026-08-22 - Learner-data backup / restore closure

- PR #9 exact head `72ecd09f261cf881581ca37f8aa429b53c46e90e` passed `lessons_lan CI` run `31946470759`.
- PR #9 was squash-merged as `8ed17074e860fb8b8dfc3e9ac4c2bd0401769987`.
- Verification proves read-only backup, non-overwriting isolated restore, SQLite integrity, table row/column fidelity, representative learner-data coverage, and canonical Flask app readability.
- `learner_data_backup_restore_20260816` advanced through `CI_VERIFIED`, `MERGED`, and `PLANNER_RECONCILED` to `COMPLETE`.
- Admin/student route-boundary and destructive-reset isolation proof is now the highest-priority executable lane.

## What remains

- Maintain the canonical test/CI gate.
- Verify admin/student route boundaries and destructive-reset isolation.
- Add TEKS coverage reporting.
- Expand admin/mastery route tests where gaps remain.
- Keep PR #5 readiness-held until its documented gates are independently met or explicitly bounded out.


## 2026-11-25 — Access boundary acceptance

PR #14 merged `59de341d38b73b292acc7fec4dc9f91e16ebb07f`; exact-head CI `45722603823` succeeded. Isolated Flask tests cover anonymous/student denial, unchanged fixture records, CLI-only reset and authorized admin edit. No production data touched. Default session signing key remains a deployment hold.


## 2026-11-25 — Session-signing source acceptance

PR #16 merged `3bdcb4657c72dd36ae174ddafc34ef5aa69298e6`; exact-head CI `45724342656` succeeded. Persistent random key, restart continuity, legacy-cookie rejection, concurrent startup and POSIX permission tests verified in isolated CI. Windows ACL, seeded account security and live deployment remain open; external pilot hold preserved.

## 2026-11-26 — Family-pilot source status reconciliation

PR #5 merged `c7b45290612df2cf53c21368fcaed7623a9ca3b4`. Earlier draft/open branch references above are historical observations, not current PR state. The merged readiness package does not authorize external or paid pilot activation; documented readiness and human gates remain controlling. No production mutation or pilot activation performed.

## 2026-11-26 — First-run provisioning integration acceptance

PR #17 merged `046cfaf64f124735513858cc8f2dff8d76a74a9c`; exact-head canonical CI `45738041920` passed. Secure first-run provisioning, atomic seeding and isolated preservation regressions integrated. Existing household credential rotation, Windows ACL, live deployment and external pilot authorization remain held; no production data modified.

## 2026-11-26 — Admin regression integration acceptance

PR #18 merged `cfa745b89f95b8d9ab0ba230471d64a30aeb9c51`; exact-head canonical CI `45738427687` passed. Authorized account rotation, invalid password rejection, scoped lesson lifecycle and preservation of unrelated records verified. Mastery threshold regressions committed separately on the current branch; canonical CI pending. Existing credential rotation, Windows ACL, live deployment and external pilot remain held.

## 2026-11-26 — Operator priority decision: maintenance-only

HomeSchool Mastery is dormant for feature delivery. The operator deprioritized the product because household learners returned to public school. Defer TEKS skill/question coverage reporting, curriculum enhancements, mastery expansion, prototype consolidation and external pilot activity until explicitly reactivated. Preserve source, existing accounts, hashes, learner records and backups; no live shutdown, data deletion, credential rotation or deployment is authorized by this decision. Retain Windows ACL, existing legacy credential rotation, deployment verification and external pilot authorization as unresolved security/operational obligations; address an actual security incident through authorized maintenance. Routine feature assignments are not eligible. Governed merged-branch retirement remains maintenance, not feature work.

Verified source checkpoint: PR #17 merged `046cfaf64f124735513858cc8f2dff8d76a74a9c` (CI `45738041920`), #18 merged `cfa745b89f95b8d9ab0ba230471d64a30aeb9c51` (CI `45738427687`), #19 merged `8c37081e5bdabb6236fa9253c754cb1d53830ab0` (CI `45739114459`). No production acceptance is claimed.
