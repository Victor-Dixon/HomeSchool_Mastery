# Roadmap — HomeSchool Mastery

> Last updated: 2026-05-25

---

## Phase 1 — Core Loop Online (Completed)

**Goal:** Stand up the foundational learning system and prove the diagnostic loop works.

| Milestone | Status |
|-----------|--------|
| Role-based login (student PIN, teacher auth) | Done |
| Student + teacher dashboards | Done |
| Skill lifecycle tracking (unseen → needs_work → mastered) | Done |
| XP system (500 XP per level) | Done |
| Achievement badges (10 badges) | Done |
| WebSocket real-time sync across devices | Done |
| data.json local persistence | Done |
| CSV export for teacher reporting | Done |
| Mobile-first responsive UI | Done |

**Exit Criteria Met:** Students can log in, take quizzes, earn XP, and Victor can monitor progress in real-time.

---

## Phase 2 — SSOT Enforcement (Current — as of April 2026)

**Goal:** Make the TEKS skill list the single source of truth (SSOT) so quiz availability and coverage track directly to the curriculum model.

| Milestone | Status |
|-----------|--------|
| TEKS skills list as canonical data source | In Progress |
| Auto-generated quizzes from skill records | In Progress |
| Manual quiz override for curated items | In Progress |
| Domain-shape checks for quiz outputs | In Progress |
| Flask LAN lessons app stabilization (lessons_lan/) | In Progress |
| Existing pytest coverage preserved as verification gate | Done |

**Exit Criteria:** Every tracked TEKS skill either has an auto-generated quiz or a curated override. Domain-shape validation prevents malformed quiz data.

---

## Phase 3 — Adaptive Diagnostics (Next)

**Goal:** Make the quiz engine smarter — adapt difficulty, prioritize gaps, and surface trends.

| Milestone | Status |
|-----------|--------|
| Difficulty ramp based on quiz history | Planned |
| Gap-prioritized sequencing (worst-first) | Planned |
| Subject/strand-level weakness trend tracking | Planned |
| Per-student difficulty calibration | Planned |

**Exit Criteria:** Quiz difficulty adjusts after consecutive correct/incorrect answers. Students see their weakest skills first. Victor can view weakness trends over time.

---

## Phase 4 — Insight & Planning

**Goal:** Turn accumulated data into actionable recommendations for Victor.

| Milestone | Status |
|-----------|--------|
| Parent/teacher intervention recommendations | Planned |
| Progress forecasts (projected mastery dates) | Planned |
| Weekly learning plans (auto-generated) | Planned |
| Weakness trend visualizations | Planned |

**Exit Criteria:** Victor receives a weekly summary with specific recommendations for each student.

---

## Phase 5 — Scale (Future)

**Goal:** Optionally extend the system beyond the household LAN.

| Milestone | Status |
|-----------|--------|
| Optional cloud sync for backup and remote access | Planned |
| Multi-home support (share curriculum across households) | Planned |
| Voice-based interaction (hands-free quizzes) | Planned |
| Additional grade-level TEKS support | Planned |

**Exit Criteria:** System can optionally sync to cloud without breaking local-first operation.

---

## Phase Progression

```
Phase 1 ──▶ Phase 2 ──▶ Phase 3 ──▶ Phase 4 ──▶ Phase 5
 (Done)     (Current)    (Next)     (Later)     (Future)
  Core        SSOT       Adaptive   Insight     Scale
  Loop      Enforcement  Diagnostics & Planning
```

Each phase builds on the prior. No phase is started until the previous phase's exit criteria are met.
