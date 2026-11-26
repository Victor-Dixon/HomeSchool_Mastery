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
- [ ] Assess and secure seeded account credentials.
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

Assess seeded-account security. PR #16 merged `3bdcb4657c72dd36ae174ddafc34ef5aa69298e6`; exact-head CI `45724342656` passed. Isolated regression tests cover persistent random signing keys, invalid configuration rejection, restart session continuity, legacy cookie rejection, concurrent startup and POSIX permissions. Windows ACL and live deployment remain unverified; seeded account password security and external pilot remain held.

## External pilot hold

PR #5 is a draft readiness-gated family-pilot package. Do not treat the document
as authorization to begin an external/paid pilot or as proof of production
readiness, demand, customers, pricing, educational efficacy, or market
validation. Its documented readiness and human gates remain controlling.

## What remains

The next readiness work is seeded-account security and live deployment acceptance,
and then the remaining
production-readiness checklist items.
