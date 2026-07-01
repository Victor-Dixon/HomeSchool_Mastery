# Product Requirements Document — HomeSchool Mastery

| Field   | Value |
|---------|-------|
| Repo    | Victor-Dixon/HomeSchool_Mastery |
| Owner   | Victor Dixon |
| Status  | Active Development — Phase 2 (SSOT-driven diagnostics stabilization) |
| Version | 2.0 |
| Updated | 2026-05-25 |

---

## Overview

HomeSchool Mastery is a **diagnostic-first learning system** built for a two-student, one-teacher homeschool household. It replaces passive curriculum tracking with an active feedback loop: diagnose gaps, focus effort, prove mastery, reward progress, repeat.

The system comprises two co-deployed applications:

1. **Mastery (Node.js)** — quiz engine, XP/badges, skill lifecycle, WebSocket real-time sync. Port 3000.
2. **Homeschool Lessons (Flask)** — daily lesson checklists, vocabulary games, spelling lab, practice items on the LAN. Port 5000.

Both apps run locally on the home network with zero cloud dependency.

---

## Problem Statement

Traditional homeschool curricula rely on linear lesson plans and periodic tests. They lack:

- **Real-time gap detection** — weaknesses hide until exam day.
- **Adaptive focus** — students waste time on already-mastered material.
- **Immediate feedback** — motivation drops without visible progress signals.
- **Teacher visibility** — Victor cannot monitor two students' live state simultaneously.

HomeSchool Mastery addresses each of these by making diagnostics the primary driver of every learning session.

---

## Goals

| # | Goal | Mechanism |
|---|------|-----------|
| G1 | Detect learning gaps in real-time | Quiz engine runs diagnostics per skill, surfaces "needs_work" items immediately |
| G2 | Focus effort where it matters | UI hides mastered content; daily workflow starts with gap review |
| G3 | Reinforce mastery through feedback loops | Skill lifecycle (unseen → needs_work → mastered) prevents assumed mastery |
| G4 | Gamify progress | XP, levels (500 XP/level), 10 achievement badges |
| G5 | Provide teacher oversight | Teacher dashboard with multi-student view, progress export, gap identification |

---

## Non-Goals

- **Cloud dependency** — the system must remain local-first; cloud sync is a future opt-in.
- **Destructive cleanup of learner history** — student data and progress records are never deleted automatically.
- **Untested changes** — no route, mastery, or quiz logic change ships without passing tests.

---

## Target Users

| User    | Role    | Grade | Context |
|---------|---------|-------|---------|
| Charlie | Student | 6th   | Takes quizzes, earns XP/badges, progresses through TEKS skill tree |
| Chris   | Student | 7th   | Same workflow, grade-appropriate TEKS skills |
| Victor  | Teacher / Admin | — | Monitors both students, controls content, exports data, assigns focus areas |

All users share the same system with **role-based views** and PIN-based login.

---

## Scope

### In Scope

- Diagnostic quiz engine (2–3 questions per skill, auto-scored)
- Skill lifecycle tracking (unseen → needs_work → mastered) with TEKS alignment
- XP, levels, and 10 achievement badges
- WebSocket real-time sync across household devices
- Teacher dashboard (multi-student view, CSV export, gap identification)
- TEKS/STAAR standards alignment for 6th and 7th grade
- Flask LAN lessons app (daily checklists, vocabulary games, spelling lab, practice)

### Out of Scope (Current Phase)

- Cloud sync / remote access
- Multi-school or multi-household support
- Advanced analytics (ML-driven predictions, cohort analysis)
- Third-party LMS integration

---

## Success Criteria

| Criterion | Target | Verification |
|-----------|--------|--------------|
| TEKS skill coverage | All 6th + 7th grade TEKS skills tracked in data model | Skill list audit against TEKS standards |
| Quiz coverage | >80% of tracked skills have associated quiz items | Script-generated coverage report |
| Real-time sync | WebSocket updates propagate within 1 second on LAN | Manual device test during daily workflow |
| Test gate | `pytest -q` passes in `lessons_lan/` before any deploy | CI or manual pre-deploy check |
| Data persistence | `data.json` survives restarts; CSV export produces valid output | Backup verification test |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                Home LAN Network                  │
│                                                  │
│  ┌──────────────────┐   ┌─────────────────────┐ │
│  │  Mastery (Node)  │   │  Lessons (Flask)     │ │
│  │  server.js :3000 │   │  run.py :5000        │ │
│  │  ─────────────── │   │  ───────────────     │ │
│  │  Quiz Engine     │   │  Lesson Checklists   │ │
│  │  Skill Lifecycle │   │  Vocabulary Games    │ │
│  │  XP / Badges     │   │  Spelling Lab        │ │
│  │  WebSocket Sync  │   │  Practice Items      │ │
│  │  Teacher Dash    │   │  Admin Routes        │ │
│  └───────┬──────────┘   └───────┬─────────────┘ │
│          │                      │                │
│          ▼                      ▼                │
│     data.json              SQLite / local DB     │
│     (persistence)          (lessons state)       │
└─────────────────────────────────────────────────┘
```

### Data Flow

1. Student logs in with PIN → role-based view loads.
2. Student takes quiz → engine scores answers → skill status transitions.
3. XP awarded → badge eligibility checked → UI updates via WebSocket.
4. Teacher views dashboard → sees aggregated progress → exports CSV.

---

## Evidence References

| Source | Location | Notes |
|--------|----------|-------|
| README.md | repo root | Rich system description, architecture, roadmap |
| AGENTS.md | repo root | Agent rules, canonical app designation |
| PRD.md (prior) | repo root | Brief original PRD |
| MASTER_TASK_LIST.md | repo root | Open/done task tracking |
| MASTER_TASK_LOG.md | repo root | Completion history |
| NEXT_UP.md | repo root | Short-term action items |
| lessons_lan/README.md | lessons_lan/ | Flask app documentation |
| tests/ | lessons_lan/ | Existing pytest coverage |
