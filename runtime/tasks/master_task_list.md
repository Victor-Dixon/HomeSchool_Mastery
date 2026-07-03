# Master Task List - HomeSchool Mastery

> Updated: 2026-07-03

## Purpose

HomeSchool Mastery is a local-first family homeschool learning platform. The
canonical app is `lessons_lan/`, a Flask LAN app for lessons, practice, games,
XP/mastery accountability, feedback, and parent/admin workflows.

## Domain

Family homeschool education and learner accountability, with TEKS/STAAR-aligned
Math and Reading/ELAR practice.

## Current priority order

### Verification and operations

- [ ] Run and preserve `cd lessons_lan && pytest -q` as the canonical
      verification gate.
- [ ] Add CI workflow for the current Python tests.
- [ ] Add data backup/export verification for `lessons_lan` learner data.
- [ ] Complete `PRODUCTION_READINESS.md` checklist items.
- [ ] Add documented smoke-test steps for household operation.

### Canonical app quality

- [ ] Expand pytest coverage for admin/mastery dashboard routes.
- [ ] Add TEKS skill/question coverage report.
- [ ] Expand Reading and Math question bank coverage with TEKS tags and item
      types.
- [ ] Formalize mastery tier map for levels 1-100 and boss gates.
- [ ] Decide whether `app/generator.py` should be wired into daily lessons or
      remain a tested utility.

### Documentation

- [ ] Add route/API reference for `lessons_lan/`.
- [ ] Add parent/admin user guide for daily operation.
- [ ] Add contributing guide for future development.
- [ ] Keep docs synchronized when canonical architecture changes.

### Data and analytics

- [ ] Build weekly progress report/export for each student.
- [ ] Add weakness trend tracking from question attempts.
- [ ] Add subject mastery visualization.
- [ ] Add historical practice/boss performance reporting.

### Future/adaptive learning

- [ ] Implement adaptive difficulty ramp based on recent answers.
- [ ] Add weak-skill prioritization from attempt history.
- [ ] Implement timed STAAR-style practice mode.
- [ ] Add streaks or additional rewards only after current XP/mastery behavior
      remains test-backed.

### Context decisions

- [ ] Decide whether the root Node prototype is maintained, integrated, or
      archived. Current canonical status: not canonical.
- [ ] Decide whether `ai_tutor/` remains a support package or integrates with
      `lessons_lan/`. Current canonical status: support package.
- [ ] If either context becomes canonical, update PRD, roadmap, domain model,
      README, AGENTS, and tests in the same change.

## Completed

- [x] Identify `lessons_lan/` as canonical implementation.
- [x] Confirm existing pytest coverage exists.
- [x] Add governance baseline artifacts (`AGENTS.md`, master task docs,
      `NEXT_UP.md`).
- [x] Add production readiness checklist file.
- [x] Document canonical app startup/shutdown/database location.
- [x] Audit README and architecture docs for stale Node-era references.
- [x] Produce synchronized domain model with entities, value objects, services,
      relationships, data flow, integrations, feature mapping, and Unknowns.
- [x] Synchronize PRD, roadmap, master task list, master task log, NextUp,
      AGENTS, README, app docs, and runtime task docs on 2026-07-03.

## What remains

The main remaining work is operational evidence: tests, CI, backup/export, TEKS
coverage reporting, and admin/mastery coverage. Adaptive diagnostics and
cross-runtime integration should wait until those foundations are documented and
test-backed.
