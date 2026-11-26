# Next Up

> Updated: 2026-11-26

**MAINTENANCE_ONLY / FEATURE_DELIVERY_DEFERRED**

No active feature assignment. Reopen only on explicit operator priority change or an authorized security/maintenance need.

## 2026-11-26 — Operator priority decision: maintenance-only

HomeSchool Mastery is dormant for feature delivery. The operator deprioritized the product because household learners returned to public school. Defer TEKS skill/question coverage reporting, curriculum enhancements, mastery expansion, prototype consolidation and external pilot activity until explicitly reactivated. Preserve source, existing accounts, hashes, learner records and backups; no live shutdown, data deletion, credential rotation or deployment is authorized by this decision. Retain Windows ACL, existing legacy credential rotation, deployment verification and external pilot authorization as unresolved security/operational obligations; address an actual security incident through authorized maintenance. Routine feature assignments are not eligible. Governed merged-branch retirement remains maintenance, not feature work.

Verified source checkpoint: PR #17 merged `046cfaf64f124735513858cc8f2dff8d76a74a9c` (CI `45738041920`), #18 merged `cfa745b89f95b8d9ab0ba230471d64a30aeb9c51` (CI `45738427687`), #19 merged `8c37081e5bdabb6236fa9253c754cb1d53830ab0` (CI `45739114459`). No production acceptance is claimed.

## Verification authority

`cd lessons_lan && python -m pytest -q`

Exact-head CI is required for application changes.
