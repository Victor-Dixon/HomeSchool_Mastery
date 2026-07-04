# Production Readiness

> Updated: 2026-07-03

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

Local/LAN homeschool app with existing test coverage. Documentation for startup,
shutdown, database location, and reset safety has been refreshed. Backup/export,
CI, and full readiness verification remain open.

## Required before household production

- [ ] Confirm all tests pass from `lessons_lan/`.
- [x] Document startup command.
- [x] Document shutdown command.
- [x] Document database location.
- [ ] Document and verify backup/export path.
- [ ] Document restore/smoke-test procedure after backup.
- [ ] Verify admin/student route boundaries with targeted tests.
- [x] Document destructive reset path as operator-only.
- [ ] Verify no destructive reset path is exposed to students.
- [ ] Add CI for the canonical test gate.

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

Back up this file before maintenance. Do not delete generated databases during
normal work.

## Verification gate

```bash
cd lessons_lan && pytest -q
```

## What remains

The next readiness work is backup/export verification, route-boundary tests, CI,
and a documented restore smoke test.
