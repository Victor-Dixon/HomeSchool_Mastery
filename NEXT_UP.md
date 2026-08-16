# Next Up

> Updated: 2026-08-16

This is the immediate executable queue. `MASTER_TASK_LIST.md` and
`runtime/tasks/master_task_list.md` remain the complete backlog; the task logs
remain append-only verified history.

## Highest-priority executable lane

### Verify learner-data backup/export and isolated restore

**Why it exists**

HomeSchool Mastery is a local-first family homeschool platform whose canonical
learner data lives in `lessons_lan/instance/homeschool.db`. The repository now
has an independently verified CI gate, so the next unresolved production-
readiness dependency is proving that learner data can be backed up, read back,
and restored safely before household production or any external pilot expands.

**Authority/source**

- `PRD.md` and `docs/PRD.md`
- `ROADMAP.md` and `docs/ROADMAP.md`
- `PRODUCTION_READINESS.md`
- `MASTER_TASK_LIST.md` and `runtime/tasks/master_task_list.md`
- merged PR #6 CI evidence recorded in the task logs

**Current state**

- `lessons_lan/` is the canonical app.
- The backup/restore verification slice is `ACTIVE` on `feat/learner-data-backup-restore-20260816`; implementation and targeted tests are present, but exact-head CI is still required before review/closeout claims.
- PR #6 added the canonical `lessons_lan CI` workflow and merged after exact-head CI success.
- PR #7 salvaged the prior test-runtime optimization onto current `master`, passed exact-head CI, and merged.
- Original PR #4 is closed without merge as superseded by PR #7.
- PR #5 remains an `ACTIVE_PR / DRAFT / READINESS_HELD` family-pilot document; it does not own canonical planners.
- `docs/planning-reconciliation-20260813` is `MERGED_STALE`.
- `feat/lessons-lan-ci-20260816` is `MERGED_STALE_BY_PR_6`; squash ancestry must not be mistaken for unique unmerged work.
- `test/app-runtime-reduction-20260813` is `SUPERSEDED_BY_PR_7`.
- `test/app-runtime-reduction-refresh-20260816` is `MERGED_STALE_BY_PR_7`.

**Blockers**

- Exact-head `lessons_lan CI` has not yet verified the active backup/restore implementation slice.

**Done evidence**

1. A documented command or test creates a backup/export from an isolated test database or explicitly safe operator path.
2. The backup is restored/read into an isolated location; live learner data is never overwritten during verification.
3. Verification checks expected tables, row counts, and important columns for canonical learner-data entities.
4. A restore smoke test proves the restored database can be opened by the canonical app/test path.
5. `PRODUCTION_READINESS.md`, planner surfaces, and task logs are reconciled from actual verification evidence.
6. Any code/test change receives exact-head `lessons_lan CI` success before merge/complete claims.

**Do not work concurrently on**

- external or paid pilot activation from PR #5 before readiness gates are satisfied;
- adaptive-learning expansion or Node/`ai_tutor/` integration;
- destructive reset/cleanup of learner data;
- resurrection of PR #4 or duplicate test-runtime optimization work.

## Following lanes

2. Verify admin/student route boundaries and prove destructive reset is unavailable to student flows.
3. Expand admin/mastery route tests where coverage gaps remain.
4. Add TEKS skill/question coverage reporting and keep complete-corpus coverage `Unknown` until measured.
5. Resolve the future status of the root Node prototype and `ai_tutor/` only after readiness foundations are proven.

## Verification authority

```bash
cd lessons_lan && python -m pytest -q
```

GitHub Actions `lessons_lan CI` is the independent CI authority for changes
under `lessons_lan/**` or the workflow itself. Exact-head CI evidence is required
for `CI_VERIFIED` claims.

Volatile SHAs and ahead/behind counts belong in the task logs as timestamped
evidence, not in this durable execution queue.
