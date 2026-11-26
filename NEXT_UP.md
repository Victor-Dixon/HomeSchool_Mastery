# Next Up

> Updated: 2026-08-22

This is the immediate executable queue. The task lists remain the complete backlog; the task logs remain append-only verified history.

## Highest-priority executable lane

### Expand admin/mastery regression coverage

PR #16 merged `3bdcb4657c72dd36ae174ddafc34ef5aa69298e6`; exact-head CI `45724342656` passed. Isolated regression tests cover persistent random signing keys, invalid configuration rejection, restart session continuity, legacy cookie rejection, concurrent startup and POSIX permissions. Windows ACL and live deployment remain unverified; existing credential rotation and external pilot remain held.

Acceptance: verify authorized account rotation and scoped lesson lifecycle in isolated fixtures, preserving unrelated accounts and learner records. Run exact-head canonical CI; do not claim broader mastery coverage without evidence.

## Following lanes

3. Add TEKS skill/question coverage reporting.
4. Resolve the future status of the root Node prototype and `ai_tutor/` only after readiness foundations are proven.

## Verification authority

```bash
cd lessons_lan && python -m pytest -q
```

Exact-head GitHub Actions evidence is required for `CI_VERIFIED` claims.

PR #17 merged `046cfaf64f124735513858cc8f2dff8d76a74a9c`; exact-head canonical CI `45738041920` passed. Secure first-run provisioning, atomic seeding and isolated preservation regressions integrated. Existing household credential rotation, Windows ACL, live deployment and external pilot authorization remain held; no production data modified.
