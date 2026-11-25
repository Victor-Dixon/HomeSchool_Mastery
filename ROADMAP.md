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

- Learner-data backup/export and isolated restore/smoke: Verified through PR #9, exact-head CI `31946470759`, merge `8ed17074e860fb8b8dfc3e9ac4c2bd0401769987` (isolated test databases; not a live household restore).

- Access-boundary verification: PR #14 merged `59de341d38b73b292acc7fec4dc9f91e16ebb07f`; exact-head `lessons_lan CI` run `45722603823` succeeded. Isolated Flask/SQLite regression coverage: anonymous/student admin request denial, unchanged records, CLI-only reset, positive admin edit. This does not establish production security; default session signing key remains a hold.

## Current

- Keep the canonical app stable and test-backed through the local pytest gate and GitHub Actions CI.
- Complete production-readiness items.
- Preserve verified backup/restore and access boundaries; resolve session-signing security before broader readiness claims.

## Next

1. Verify secure session-signing configuration and reject known default keys.
2. Expand admin/mastery tests where evidence is still missing.
3. Add TEKS/STAAR coverage reporting.
4. Keep PR #5 family-pilot work readiness-held until its documented gates are satisfied or explicitly bounded out.

## Later

- Adaptive difficulty and weak-skill sequencing.
- Formal mastery tier map for levels/gates.
- Decision on root Node prototype and `ai_tutor/` support package status.
