# Next Up

> Updated: 2026-08-22

This is the immediate executable queue. The task lists remain the complete backlog; the task logs remain append-only verified history.

## Highest-priority executable lane

### Verify secure session-signing configuration

PR #14 merged `59de341d38b73b292acc7fec4dc9f91e16ebb07f`; exact-head `lessons_lan CI` run `45722603823` succeeded. Isolated Flask/SQLite regression coverage: anonymous/student admin request denial, unchanged records, CLI-only reset, positive admin edit. This does not establish production security; default session signing key remains a hold.

Acceptance: establish supported configuration, reject known/default signing keys for deployment, preserve isolated test operation and session persistence across restart, and run exact-head canonical CI. No production configuration or learner data changes without authority.

## Following lanes

2. Expand admin/mastery route tests where coverage gaps remain.
3. Add TEKS skill/question coverage reporting.
4. Resolve the future status of the root Node prototype and `ai_tutor/` only after readiness foundations are proven.

## Verification authority

```bash
cd lessons_lan && python -m pytest -q
```

Exact-head GitHub Actions evidence is required for `CI_VERIFIED` claims.
