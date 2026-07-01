# Next Up

> Updated: 2026-05-25

---

## 1. Audit README for stale Node-era architecture references

**AC:** README accurately reflects the dual-app reality (Node mastery + Flask lessons_lan), with no misleading single-app language.

## 2. Document Flask LAN startup/shutdown path

**AC:** `lessons_lan/README.md` contains complete setup instructions — venv creation, dependency install, run command, graceful shutdown, and LAN access URLs.

## 3. Add data backup/export verification test

**AC:** A test in `lessons_lan/tests/` exports CSV, reads it back, and verifies row count and column content match expected output.

## 4. Expand admin mastery dashboard tests

**AC:** Admin routes in `lessons_lan/` have >80% test coverage; all dashboard GET/POST endpoints return expected status codes and content.

## 5. Add TEKS skill coverage report generator

**AC:** A script outputs the percentage of tracked TEKS skills that have associated quiz items, broken down by subject and grade.

## 6. Implement adaptive difficulty ramp for quiz engine

**AC:** After 3 consecutive correct answers on a skill strand, the next quiz increases in difficulty (longer questions, fewer hints). After 2 consecutive failures, difficulty decreases.

## 7. Add production readiness checklist for household deployment

**AC:** A `PRODUCTION_READINESS.md` file exists covering: pre-deploy checks, data backup, network config, startup commands, smoke tests, and rollback steps.

## 8. Add CI workflow for pytest on lessons_lan

**AC:** `.github/workflows/ci.yml` runs `pytest -q` in `lessons_lan/` on push/PR to main. Workflow passes on current test suite.

## 9. Add WebSocket reconnection handling for mobile devices

**AC:** Client-side WebSocket code auto-reconnects within 5 seconds after disconnect, with exponential backoff up to 30 seconds.

## 10. Create parent progress report email/export feature

**AC:** Victor can generate a weekly summary per student (skills mastered, quizzes taken, XP earned, current gaps) and export it as PDF or formatted text.
