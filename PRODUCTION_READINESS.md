# Production Readiness

> Updated: 2026-08-22

## What is this project?

HomeSchool_Mastery is a local-first family homeschool learning platform. The
canonical app is `lessons_lan/`, a Flask LAN app for lessons, practice, games,
XP/mastery accountability, feedback, and parent/admin workflows.

## Why does it exist?

It supports safe, simple household learning operations on a home network without
requiring cloud services.

## Domain

Family homeschool education and learner accountability, with TEKS/STAAR-aligned
Math and Reading/ELAR practice.

## Current status

The canonical app now has independently verified GitHub Actions CI in addition
to the local pytest gate. Production readiness is still incomplete because
learner-data backup/export and isolated restore/smoke behavior are independently
verified through PR #9. Isolated route-safety checks are verified through PR #14; signing-key source acceptance is verified through PR #16; live deployment remains open.

## Required before household production

- [x] Confirm the canonical test gate passes in independent CI. PR #6 exact-head `lessons_lan CI` run `31931001139` succeeded.
- [x] Document startup command.
- [x] Document shutdown command.
- [x] Document database location.
- [x] Document and verify backup/export path through PR #9.
- [x] Document and verify isolated restore/smoke-test procedure after backup through PR #9.
- [x] Verify admin/student route boundaries in isolated tests (PR #14, CI `45722603823`).
- [x] Verify non-default signing key and reject unsafe configuration in isolated CI (PR #16).
- [ ] Verify Windows signing-key ACL and live deployment configuration.
- [x] Secure first-run account provisioning in isolated CI (PR #17).
- [ ] Verify explicit rotation of existing legacy household credentials before live exposure.
- [x] Document destructive reset path as operator-only.
- [x] Verify no destructive reset path is exposed to students in isolated tests (PR #14).
- [x] Add CI for the canonical test gate through PR #6.

## Startup

See `lessons_lan/README.md`. Summary:

```bash
cd lessons_lan
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Shutdown

For terminal runs, press `Ctrl+C` in the terminal running `python run.py`. For
autostart-managed runs, use the matching uninstall script in
`lessons_lan/autostart/` and stop the currently running Python process if needed.

## Data location

Canonical learner data is stored in:

```text
lessons_lan/instance/homeschool.db
```

Back up this file before maintenance. Do not delete or overwrite real learner
data during verification.

## Verification gate

Local:

```bash
cd lessons_lan && python -m pytest -q
```

Independent CI:

- Workflow: `.github/workflows/ci.yml` (`lessons_lan CI`)
- PR #6 exact-head run `31931001139`: success
- PR #7 exact-head run `31934385959`: success after salvaging the prior test-runtime optimization onto current master
- PR #9 exact-head run `31946470759`: success for learner-data backup and isolated restore

## Current readiness lane

PR #17 merged `046cfaf64f124735513858cc8f2dff8d76a74a9c`; exact-head canonical CI `45738041920` passed. Secure first-run provisioning, atomic seeding and isolated preservation regressions integrated. Existing household credential rotation, Windows ACL, live deployment and external pilot authorization remain held; no production data modified. Next source lane: admin/mastery regression coverage.

## External pilot hold

The readiness-gated family-pilot package merged in PR #5 (`c7b45290612df2cf53c21368fcaed7623a9ca3b4`); external activation remains held. Do not treat the document
as authorization to begin an external/paid pilot or as proof of production
readiness, demand, customers, pricing, educational efficacy, or market
validation. Its documented readiness and human gates remain controlling.

## What remains

The next readiness work is admin/mastery regression coverage, existing credential rotation and live deployment acceptance,
and then the remaining
production-readiness checklist items.

PR #17 merged `046cfaf64f124735513858cc8f2dff8d76a74a9c`; exact-head canonical CI `45738041920` passed. Secure first-run provisioning, atomic seeding and isolated preservation regressions integrated. Existing household credential rotation, Windows ACL, live deployment and external pilot authorization remain held; no production data modified.

## 2026-11-26 — Operator priority decision: maintenance-only

HomeSchool Mastery is dormant for feature delivery. The operator deprioritized the product because household learners returned to public school. Defer TEKS skill/question coverage reporting, curriculum enhancements, mastery expansion, prototype consolidation and external pilot activity until explicitly reactivated. Preserve source, existing accounts, hashes, learner records and backups; no live shutdown, data deletion, credential rotation or deployment is authorized by this decision. Retain Windows ACL, existing legacy credential rotation, deployment verification and external pilot authorization as unresolved security/operational obligations; address an actual security incident through authorized maintenance. Routine feature assignments are not eligible. Governed merged-branch retirement remains maintenance, not feature work.

Verified source checkpoint: PR #17 merged `046cfaf64f124735513858cc8f2dff8d76a74a9c` (CI `45738041920`), #18 merged `cfa745b89f95b8d9ab0ba230471d64a30aeb9c51` (CI `45738427687`), #19 merged `8c37081e5bdabb6236fa9253c754cb1d53830ab0` (CI `45739114459`). No production acceptance is claimed.
