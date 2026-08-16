# Roadmap - Summary

> Canonical expanded roadmap: `docs/ROADMAP.md`
> Updated: 2026-08-16

## What is this project?

HomeSchool_Mastery is a local-first family homeschool learning platform. The
canonical implementation is the Flask LAN app in `lessons_lan/`.

## Why does it exist?

It supports daily lessons, practice, games, XP/mastery accountability, feedback,
and parent/admin operations on a home LAN.

## Domain

Family homeschool education and learner accountability, with TEKS/STAAR-aligned
Math and Reading/ELAR practice.

## Completed

- `lessons_lan/` identified as canonical.
- Documentation-first domain model audit completed.
- PRD, roadmap, master task docs, NEXT_UP, AGENTS, README, and app docs aligned around the canonical Flask implementation.
- Canonical `lessons_lan CI` added and exact-head verified through PR #6.
- Test-runtime optimization salvaged from stale PR #4, reverified on current master through PR #7, and merged; PR #4 closed as superseded.

## Current

- Keep the canonical app stable and test-backed through the local pytest gate and GitHub Actions CI.
- Complete production-readiness items.
- Preserve learner data and prove backup/export plus isolated restore behavior before broader pilot/readiness claims.

## Next

1. Verify learner-data backup/export and isolated restore/smoke behavior.
2. Verify admin/student route boundaries and destructive-reset isolation.
3. Expand admin/mastery tests where evidence is still missing.
4. Add TEKS/STAAR coverage reporting.
5. Keep PR #5 family-pilot work readiness-held until its documented gates are satisfied or explicitly bounded out.

## Later

- Adaptive difficulty and weak-skill sequencing.
- Formal mastery tier map for levels/gates.
- Decision on root Node prototype and `ai_tutor/` support package status.
