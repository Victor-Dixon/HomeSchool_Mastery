# Master Task Log - HomeSchool Mastery

> Chronological record of completed tasks, milestones, and significant events.
> Updated: 2026-08-22

This file is the expanded dated evidence/history log. It answers: "What
happened, when, and why?"

## Project context

HomeSchool Mastery is a local-first family homeschool learning platform. The
canonical implementation is `lessons_lan/`, a Flask LAN app for daily lessons,
practice, games, XP/mastery accountability, feedback, and parent/admin
workflows.

Domain: family homeschool education and learner accountability, with
TEKS/STAAR-aligned Math and Reading/ELAR practice.

## Earlier history retained from prior docs

### Phase 1 notes

- A root Node mastery prototype exists with role-based login, skill quiz logic,
  XP/badge concepts, WebSocket sync, and `data.json` persistence if run.
- Current canonical status of that runtime is not established by the 2026-07-03
  audit; it is documented as present but not canonical.

### 2026-04-06

- Prior docs declared Phase 2 as SSOT-driven diagnostics stabilization.
- Current audit keeps SSOT/TEKS coverage as open unless verified by current
  `lessons_lan/` implementation and tests.

### 2026-05-07

- Added governance baseline artifacts (`AGENTS.md`, `MASTER_TASK_LIST.md`,
  `MASTER_TASK_LOG.md`, `NEXT_UP.md`).
- Classified `lessons_lan/` as canonical implementation.
- Preserved existing pytest coverage as verification gate.
- Noted that the root README contained older Node-era architecture notes.

### 2026-05-25

- Production readiness documentation refresh created or updated:
  - `docs/PRD.md`
  - `docs/ROADMAP.md`
  - `docs/DOMAIN_MODEL.md`
  - `NEXT_UP.md`
  - `runtime/tasks/master_task_list.md`
  - `runtime/tasks/master_task_log.md`
- Follow-up audit found those docs still overrepresented older Node-era
  architecture and underrepresented shipped `lessons_lan/` entities.

## 2026-07-03

- Completed documentation-first audit of current docs and implementation.
- Established `docs/README.md` as the documentation index.
- Replaced the stale domain model with a `lessons_lan/`-centered model covering:
  core domain, subdomains, entities, value objects, services, relationships,
  data flow, user interactions, external integrations, feature mapping, and
  Unknowns.
- Updated PRD and roadmap pairs so root summaries and expanded docs agree.
- Updated task list/log pairs and `NEXT_UP.md` so completed documentation work
  is marked done and remaining work is explicit.
- Updated `AGENTS.md`, `README.md`, `lessons_lan/README.md`,
  `lessons_lan/PASSDOWN.md`, `lessons_lan/TASKLIST.md`,
  `PRODUCTION_READINESS.md`, `PROJECT_STRUCTURE_TREE.md`,
  `CONSOLIDATION_MANIFEST.md`, and parity documentation for consistency.
- Marked the root Node runtime as present but not canonical.
- Marked `ai_tutor/` as a present support package, not shared canonical
  persistence for `lessons_lan/`.
- Captured the recommended GitHub repository description in docs because the
  authenticated environment available at that audit could inspect but not apply
  repository metadata.

## 2026-08-13

- Reconciled the stranded local planning-standardization commit `d4d18e7` onto
  current remote `origin/master` without overwriting PR #2's documentation
  domain-model work.
- Standardized planning-file roles across the root summary docs and expanded
  runtime task docs.
- Kept `NEXT_UP.md` as the immediate execution queue and left broader backlog in
  the task-list files.
- No product/source/runtime behavior was changed.

## 2026-08-16 - Canonical CI established

- PR #6 exact head:
  `997e4dd4402357a7d9c08d26c237be4201aa963b`.
- `lessons_lan CI` run `31931001139` completed with conclusion `success` at
  that exact head.
- PR #6 was squash-merged as
  `bad04a1d6e643663f248982678c13e40c8c93e89`.
- The workflow installs canonical runtime/test requirements and runs
  `python -m pytest -q` from `lessons_lan/` for relevant PR/master changes.
- The CI task is therefore accepted and merged; operational learner-data
  backup/export verification becomes the next readiness dependency.

## 2026-08-16 - Test-runtime optimization salvaged from PR #4

- Original PR #4 had one unique commit touching only
  `lessons_lan/pytest.ini` and `lessons_lan/tests/test_app.py`.
- Because PR #4 predated the new CI-enabled master, its unique two-file intent
  was copied onto fresh branch `test/app-runtime-reduction-refresh-20260816`
  rather than merging the stale branch wholesale.
- Refreshed PR #7 exact head:
  `681d86adc273f4fff0410445ee7eb0417a6c311b`.
- Exact-head `lessons_lan CI` run `31934385959` completed successfully.
- PR #7 was squash-merged as
  `89c7c6e1cf4b908f111fa627e11577f3930e2fcf`.
- Original PR #4 was closed without merge as superseded; its conversation
  records the replacement PR and verification evidence.

## 2026-08-16 - Branch and ownership snapshot

Against canonical master `89c7c6e1cf4b908f111fa627e11577f3930e2fcf`:

- `docs/family-pilot-readiness-20260816`: 1 ahead / 2 behind; PR #5 remains
  `ACTIVE_PR / DRAFT / READINESS_HELD`; unique diff is one family-pilot
  readiness document.
- `docs/planning-reconciliation-20260813`: 0 ahead / 4 behind;
  `MERGED_STALE`.
- `feat/lessons-lan-ci-20260816`: raw ancestry 1 ahead / 2 behind because PR #6
  was squash-merged; `MERGED_STALE_BY_PR_6`.
- `test/app-runtime-reduction-20260813`: raw ancestry 1 ahead / 3 behind, but
  its unique file-level value was ported through PR #7; `SUPERSEDED_BY_PR_7`.
- `test/app-runtime-reduction-refresh-20260816`: raw ancestry 2 ahead / 1 behind
  because PR #7 was squash-merged; `MERGED_STALE_BY_PR_7`.
- No branch was deleted. Branch deletion remains gated on immediate current-state
  revalidation and a branch-deletion-capable path.

### 2026-08-22 - Learner-data backup / restore closure

- PR #9 exact head `72ecd09f261cf881581ca37f8aa429b53c46e90e` passed `lessons_lan CI` run `31946470759`.
- PR #9 was squash-merged as `8ed17074e860fb8b8dfc3e9ac4c2bd0401769987`.
- Verification proves read-only backup, non-overwriting isolated restore, SQLite integrity, table row/column fidelity, representative learner-data coverage, and canonical Flask app readability.
- `learner_data_backup_restore_20260816` advanced through `CI_VERIFIED`, `MERGED`, and `PLANNER_RECONCILED` to `COMPLETE`.
- Admin/student route-boundary and destructive-reset isolation proof is now the highest-priority executable lane.

## Current remaining work

- Maintain the canonical local + CI test gate.
- Verify route boundaries and destructive-reset isolation.
- Add TEKS coverage reporting.
- Expand admin/mastery route tests where gaps remain.
- Keep PR #5 readiness-held until its documented gates are proven or explicitly bounded out.
- Decide future status of root Node prototype and `ai_tutor/` support package only after readiness foundations are stable.


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
