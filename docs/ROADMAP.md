# Roadmap - HomeSchool Mastery

> Last updated: 2026-07-03

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
- Current product focus: stabilize and document the canonical LAN app before
  expanding adaptive diagnostics or cross-runtime features.

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
| Synchronize PRD, roadmap, task list, task log, NextUp, AGENTS, README | Done |
| Document startup/shutdown/database location | Done in `lessons_lan/README.md` |
| Verify targeted tests after documentation sync | Pending in current branch until tests run |
| Add backup/export verification for learner data | Open |
| Add CI for current tests | Open |
| Complete production readiness checklist | Open |

Exit criteria:

- New contributors can identify the canonical app and domain model without
  additional explanation.
- `cd lessons_lan && pytest -q` passes.
- Production readiness docs cover startup, shutdown, database location, backup,
  smoke tests, rollback/reset boundaries, and route separation.

## Phase 3 - Mastery coverage and admin confidence (Next)

Goal: strengthen evidence around TEKS/STAAR practice and parent/admin workflows.

| Milestone | Status |
|---|---|
| TEKS skill coverage report | Open |
| Question bank expansion with TEKS tags and item types | Open |
| Admin/mastery dashboard test expansion | Open |
| Backup/export verification test | Open |
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

## What remains

The next work should focus on operational safety and evidence:

1. Run and document tests for the current branch.
2. Add backup/export verification.
3. Add CI for `lessons_lan` tests.
4. Add TEKS coverage reporting.
5. Expand admin/mastery tests.

Do not advance adaptive or integration work by assuming behavior from the Node
prototype or `ai_tutor/`; either wire it into the canonical app with tests or
document it as separate support/legacy behavior.
