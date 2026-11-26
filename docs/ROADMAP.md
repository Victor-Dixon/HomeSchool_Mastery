# Roadmap - HomeSchool Mastery

> Last updated: 2026-08-16

## What is this project?

HomeSchool Mastery is a local-first family homeschool learning platform. The
canonical implementation is the Flask LAN app in `lessons_lan/`.

## Why does it exist?

It exists to make daily homeschool work visible, practice-driven, motivating,
and locally operable for students and a parent/admin.

## Domain

Family homeschool education and learner accountability, with TEKS/STAAR-aligned
Math and Reading/ELAR practice. Unknowns are tracked explicitly in the PRD and
domain model.

## Current status

- Canonical app: `lessons_lan/` Flask/Jinja/SQLite LAN app.
- Support/prototype contexts: root Node app and `ai_tutor/`.
- Documentation audit: completed and synchronized on 2026-07-03.
- Canonical GitHub Actions CI: established and exact-head verified through PR #6.
- Test-runtime optimization: revalidated on current master and merged through PR #7; old PR #4 closed as superseded.
- Current product focus: seeded-account security; backup/restore, access-boundary and signing-key isolated acceptance are complete. PR #16 merged `3bdcb4657c72dd36ae174ddafc34ef5aa69298e6`; exact-head CI `45724342656` passed. Isolated regression tests cover persistent random signing keys, invalid configuration rejection, restart session continuity, legacy cookie rejection, concurrent startup and POSIX permissions. Windows ACL and live deployment remain unverified; seeded account password security and external pilot remain held.

## Phase 1 - Canonical app baseline (Completed)

Goal: establish the current source of truth and preserve existing behavior.

| Milestone | Status |
|---|---|
| Identify `lessons_lan/` as canonical implementation | Done |
| Preserve existing pytest coverage as verification gate | Done |
| Document current app operations | Done; ongoing refinement |
| Preserve local-first learner data model | Done |
| Keep parent/admin routes separate from student routes | Done; continue testing |

## Phase 2 - Documentation and production readiness (Current)

Goal: make the repository understandable and safe to operate from docs alone.

| Milestone | Status |
|---|---|
| Documentation-first domain model audit | Done |
| Synchronize PRD, roadmap, task list, task log, NEXT_UP, AGENTS, README | Done; maintain with state changes |
| Document startup/shutdown/database location | Done in `lessons_lan/README.md` |
| Verify canonical test gate in independent CI | Done through PR #6; exact-head run `31931001139` succeeded |
| Add CI for current tests | Done through PR #6 |
| Salvage/reverify prior test-runtime optimization | Done through PR #7; exact-head run `31934385959` succeeded |
| Add backup/export verification for learner data | Done; PR #9, CI `31946470759` |
| Add isolated restore/smoke verification | Done; PR #9, isolated fixture, merge `8ed17074` |
| Complete remaining production readiness checklist | Open |

Exit criteria:

- New contributors can identify the canonical app and domain model without additional explanation.
- `cd lessons_lan && python -m pytest -q` remains green and relevant pull requests receive exact-head CI evidence.
- Production readiness docs cover startup, shutdown, database location, backup, restore/smoke tests, rollback/reset boundaries, and route separation.
- Learner-data backup/export and isolated restore are independently verified before readiness claims.

## Phase 3 - Mastery coverage and admin confidence (Next)

Goal: strengthen evidence around TEKS/STAAR practice and parent/admin workflows.

| Milestone | Status |
|---|---|
| TEKS skill coverage report | Open |
| Question bank expansion with TEKS tags and item types | Open |
| Admin/mastery dashboard test expansion | Open |
| Route-boundary / destructive-reset isolation proof | Done in isolated CI; PR #14, run `45722603823` |
| API/route reference for canonical app | Open |

## Phase 4 - Adaptive learning improvements (Later)

Goal: make practice sequencing more responsive to learner evidence.

| Milestone | Status |
|---|---|
| Difficulty ramp based on recent answers | Planned |
| Weak-skill prioritization from attempt history | Planned |
| Lesson practice generation using recent misses | Planned |
| Formal tier map for levels 1-100 and gates | Planned |

## Phase 5 - Context decisions and optional integrations (Future)

Goal: decide how non-canonical contexts should evolve.

| Milestone | Status |
|---|---|
| Decide Node prototype status: archive, maintain separately, or integrate | Unknown/open |
| Decide `ai_tutor/` status: support package or canonical integration | Unknown/open |
| Optional cloud backup/sync without breaking local-first operation | Planned, not current scope |
| Additional grade-level TEKS support | Planned, not current scope |

## Active external/revenue hold

PR #5 contains a bounded family-pilot readiness document and remains
`DRAFT / READINESS_HELD`. Its existence does not prove production readiness,
market validation, customers, pricing, educational efficacy, or authorization to
begin external outreach. Advance it only when its documented readiness/human
gates are satisfied or explicitly bounded out.

## What remains

The next work should focus on operational safety and evidence:

1. Assess seeded-account security and preserve verified route/signing boundaries.
2. Add TEKS coverage reporting.
3. Expand admin/mastery tests where gaps remain.

Do not advance adaptive or integration work by assuming behavior from the Node
prototype or `ai_tutor/`; either wire it into the canonical app with tests or
document it as separate support/legacy behavior.
