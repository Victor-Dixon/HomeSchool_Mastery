# Next Up

> Updated: 2026-08-22

This is the immediate executable queue. The task lists remain the complete backlog; the task logs remain append-only verified history.

## Highest-priority executable lane

### Verify admin/student route boundaries and destructive-reset isolation

**Why it exists**

Learner-data backup and isolated restore are now verified and merged through PR #9. The next production-readiness dependency is proving that student flows cannot reach administrative or destructive-reset behavior.

**Authority/source**

- `PRD.md` and `docs/PRD.md`
- `ROADMAP.md` and `docs/ROADMAP.md`
- `PRODUCTION_READINESS.md`
- `MASTER_TASK_LIST.md` and `runtime/tasks/master_task_list.md`
- PR #9 merge and exact-head CI evidence in the task logs

**Current state**

- `lessons_lan/` is canonical.
- PR #9 exact head `72ecd09f261cf881581ca37f8aa429b53c46e90e` passed `lessons_lan CI` run `31946470759` and squash-merged as `8ed17074e860fb8b8dfc3e9ac4c2bd0401769987`.
- PR #5 remains `DRAFT / READINESS_HELD` and does not own canonical planners.

**Done evidence**

1. Targeted tests prove student sessions cannot access admin-only routes.
2. Destructive reset remains unavailable through student flows.
3. Authorized admin behavior remains functional.
4. Planner and readiness surfaces are reconciled from test evidence.
5. Any code/test change receives exact-head `lessons_lan CI` success before merge or completion claims.

**Do not work concurrently on**

- external or paid pilot activation from PR #5;
- destructive cleanup of learner data;
- adaptive-learning or Node/`ai_tutor/` integration.

## Following lanes

2. Expand admin/mastery route tests where coverage gaps remain.
3. Add TEKS skill/question coverage reporting.
4. Resolve the future status of the root Node prototype and `ai_tutor/` only after readiness foundations are proven.

## Verification authority

```bash
cd lessons_lan && python -m pytest -q
```

Exact-head GitHub Actions evidence is required for `CI_VERIFIED` claims.
