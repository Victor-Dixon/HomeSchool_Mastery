# Next Up

> Updated: 2026-08-22

This is the immediate executable queue. The task lists remain the complete backlog; the task logs remain append-only verified history.

## Highest-priority executable lane

### Assess seeded-account security

PR #16 merged `3bdcb4657c72dd36ae174ddafc34ef5aa69298e6`; exact-head CI `45724342656` passed. Isolated regression tests cover persistent random signing keys, invalid configuration rejection, restart session continuity, legacy cookie rejection, concurrent startup and POSIX permissions. Windows ACL and live deployment remain unverified; seeded account password security and external pilot remain held.

Acceptance: inspect first-run account seeding, login and password reset paths; determine how to eliminate predictable credentials without breaking existing household access or modifying live data. Verify any authorized repair against isolated fixtures and canonical CI. Preserve external pilot, Windows ACL and live deployment holds.

## Following lanes

2. Expand admin/mastery route tests where coverage gaps remain.
3. Add TEKS skill/question coverage reporting.
4. Resolve the future status of the root Node prototype and `ai_tutor/` only after readiness foundations are proven.

## Verification authority

```bash
cd lessons_lan && python -m pytest -q
```

Exact-head GitHub Actions evidence is required for `CI_VERIFIED` claims.
