# Production Readiness

## Current Status

Local/LAN homeschool app with existing test coverage.

## Required Before Household Production

- [ ] Confirm all tests pass from lessons_lan/.
- [ ] Document startup command.
- [ ] Document shutdown command.
- [ ] Document database location.
- [ ] Document backup/export path.
- [ ] Verify admin/student route boundaries.
- [ ] Verify no destructive reset path is exposed to students.

## Verification Gate

cd lessons_lan && pytest -q
