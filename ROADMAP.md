# Roadmap - Summary

> Canonical expanded roadmap: `docs/ROADMAP.md`
> Updated: 2026-07-03

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
- PRD, roadmap, master task docs, NextUp, AGENTS, README, and app docs aligned
  around the canonical Flask implementation.

## Current

- Keep the canonical app stable and test-backed.
- Complete production readiness items.
- Preserve learner data and document operator-only reset/backup workflows.

## Next

1. Run and maintain `cd lessons_lan && pytest -q` as the verification gate.
2. Add backup/export verification for learner data.
3. Add CI for current tests.
4. Expand TEKS/STAAR coverage reporting.
5. Improve parent/admin mastery workflow tests.

## Later

- Adaptive difficulty and weak-skill sequencing.
- Formal mastery tier map for levels/gates.
- Decision on root Node prototype and `ai_tutor/` support package status.
