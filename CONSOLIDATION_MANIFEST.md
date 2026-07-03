# Consolidation Manifest

> Updated: 2026-07-03

## Repo role

Family homeschool mastery platform.

## What this project is

HomeSchool_Mastery is a local-first family homeschool learning platform for
daily lessons, TEKS/STAAR-aligned practice, learning games, XP/mastery
accountability, feedback, and parent/admin workflows.

## Domain

Family homeschool education and learner accountability.

## Canonical implementation

```text
lessons_lan/
```

## Current classification

PROMOTE / ACTIVE

## Completed

- Canonical implementation identified as `lessons_lan/`.
- Documentation-first domain model audit completed on 2026-07-03.
- Root README and governance docs reconciled with the canonical Flask app.

## Remaining

- Add CI, backup/export verification, TEKS coverage reporting, and expanded
  admin/mastery tests.
- Decide whether the root Node prototype and `ai_tutor/` support package should
  remain separate, be integrated, or be archived.

## Notes

The root Node prototype and `ai_tutor/` package are present but non-canonical.
Do not use them to infer canonical `lessons_lan/` behavior without explicit
test-backed integration.
