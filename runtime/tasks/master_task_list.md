# Master Task List — HomeSchool Mastery

> Updated: 2026-05-25

---

## Core Features

- [ ] Improve quiz engine question variety (synonyms, reworded prompts)
- [ ] Implement adaptive difficulty ramp (increase after 3 correct, decrease after 2 failures)
- [ ] Add gap-prioritized quiz sequencing (weakest skills surface first)
- [ ] Support multi-question quiz types (multiple choice, fill-in-the-blank, matching)
- [ ] Add skill regression detection (flag mastered skills that show retention loss)
- [ ] Implement timed quiz mode for STAAR test prep simulation

## Infrastructure

- [ ] Add CI workflow (`.github/workflows/ci.yml` — pytest on push/PR)
- [ ] Create household deployment guide (`PRODUCTION_READINESS.md`)
- [ ] Add data backup verification test (export → read-back → validate)
- [ ] Document Flask LAN startup/shutdown path in `lessons_lan/README.md`
- [ ] Add health check endpoint to both apps (`/health`)
- [ ] Add structured logging (JSON log lines with timestamp, level, event)

## Testing

- [ ] Expand pytest coverage for admin mastery dashboard routes (>80%)
- [ ] Add Node.js test framework for `server.js` quiz engine
- [ ] Create integration test: full quiz flow (login → quiz → score → skill update)
- [ ] Add WebSocket connection/reconnection tests
- [ ] Add data.json schema validation test
- [ ] Add TEKS skill coverage report (% skills with quiz items)

## Documentation

- [ ] Audit README for stale Node-era architecture references
- [ ] Create architecture diagram (both apps, data flow, network topology)
- [ ] Write teacher/parent user guide (daily workflow, dashboard usage, export)
- [ ] Document API surface for both apps (routes, params, responses)
- [ ] Add contributing guide for future development

## Gamification

- [ ] Add streak system (consecutive daily logins/quiz sessions)
- [ ] Add challenge mode (head-to-head quizzes between Charlie and Chris)
- [ ] Add new badge tier (beyond current 10 badges)
- [ ] Add XP multiplier events (bonus XP weekends, subject-focus days)
- [ ] Add progress milestone celebrations (level-up animations, sound effects)

## Data & Analytics

- [ ] Build weekly progress report generator (per student)
- [ ] Add weakness trend tracking (skills stuck in needs_work over time)
- [ ] Create subject mastery heatmap visualization
- [ ] Add export improvements (PDF report, formatted summary)
- [ ] Add historical quiz performance graphs
- [ ] Add TEKS coverage gap report (skills with no quiz items)

---

## Completed

- [x] Identify `lessons_lan/` as canonical implementation
- [x] Confirm existing pytest coverage exists
- [x] Add governance baseline artifacts (AGENTS.md, MASTER_TASK_LIST.md, MASTER_TASK_LOG.md)
- [x] Phase 1 core loop: role-based login, dashboards, skill lifecycle, XP/badges, WebSocket sync
- [x] Production readiness documentation refresh (2026-05-25)
