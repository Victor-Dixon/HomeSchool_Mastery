# 🏆 Homeschool Mastery

*A real-time, diagnostic-first learning system for Charlie, Chris, and Victor*

---

## 🎯 Mission

This system is a **learning optimization engine**, not a basic homeschool tracker.

It exists to:

* Detect learning gaps in real-time
* Focus effort only where it matters
* Reinforce mastery through feedback loops
* Turn progress into a visible, motivating system (XP, levels, badges)

---

## 🧠 Core System Loop

```
Diagnose → Identify Gaps → Focus → Master → Reward → Repeat
```

This loop is enforced through:

* Quiz engine (diagnostics)
* Skill status transitions
* Focus-driven UI
* XP + badge feedback system

---

## 👨‍👦 Users

| User    | Role          | Function                |
| ------- | ------------- | ----------------------- |
| Charlie | Student (6th) | Skill mastery + quizzes |
| Chris   | Student (7th) | Skill mastery + quizzes |
| Victor  | Teacher       | Oversight + control     |

Each user operates inside the same system with **role-based views**.

---

## 📚 Data Model (SSOT)

All skills are derived from TEKS checklists (6th + 7th grade). 

Each skill follows a lifecycle:

```json
{
  "status": "unseen → needs_work → mastered"
}
```

---

## ⚙️ System Architecture

### 🧩 Frontend

* Single-page app (`app.html`)
* Mobile-first UI
* Gamified UX (XP, badges, levels) 

---

### 🔌 Backend

* Node.js server (`server.js`)
* WebSocket sync (real-time updates across devices)
* No external dependencies

---

### 💾 Data Layer

* `data.json` (local persistence)
* Survives restarts
* Exportable to CSV

---

## 🔥 Core Features

### 🎯 Diagnostic Quiz Engine

* 2–3 questions per skill
* Determines mastery automatically
* Drives all progression

---

### 🧠 Skill Tracking System

Each skill can be:

* ❌ Needs Work
* ⚠️ In Progress
* ✅ Mastered

---

### ⚡ Real-Time Sync

* Updates instantly across devices
* Works on same WiFi network
* No refresh needed

---

### 🎮 Gamification Layer

* XP per action
* Level system (500 XP per level)
* 10 achievement badges:

  * First Win
  * On Fire
  * Scholar
  * Legend
  * Math Wizard
  * Word Master
  * Perfectionist
  * Grinder
  * Comeback Kid
  * Unstoppable 

---

### 🧑‍🏫 Teacher Dashboard

Victor can:

* View both students simultaneously
* Track progress by subject
* Export CSV for reporting
* Monitor mastery distribution

---

## 📱 Usage Flow

### Student

1. Login with PIN
2. Take quizzes OR mark skills
3. Earn XP + badges
4. Progress through levels

---

### Teacher

1. Login as Victor
2. View live progress
3. Identify weak areas
4. Export data

---

## 🔁 Daily Workflow

| Time   | Action                 |
| ------ | ---------------------- |
| 5 min  | Open app + review gaps |
| 20 min | Teach weak skills      |
| 5 min  | Quiz + update mastery  |

---

## 🧬 What Makes This Different

This is not:

* ❌ A checklist
* ❌ A passive curriculum
* ❌ A grading system

This **is**:

* ✅ A diagnostic engine
* ✅ A feedback loop system
* ✅ A real-time learning optimizer

---

## ⚠️ System Rules (Critical)

1. Diagnostics drive all decisions
2. Focus on “Needs Work” only
3. Mastery must be proven, not assumed
4. Feedback must be immediate (XP, badges)
5. System must remain fast and frictionless

---

## 🚀 Setup

```bash
cd homeschool
node server.js
```

Open on any device via local network:

```
http://<your-ip>:3000
```

---

## 📁 Project Structure

This repository contains **three** apps that share the same family deployment but do not share a runtime:

1. **Mastery (Node.js)** — diagnostic-first skills, XP, WebSocket sync — run from the repo root; default **port 3000** (`node server.js`).
2. **Homeschool Lessons (Flask)** — daily lesson checklist, practice, spelling lab, vocabulary games on the LAN — lives in **`lessons_lan/`**; default **port 5000**.
3. **AI Tutor (Flask + Discord)** — Ollama-powered homework help API and Discord bot with TEKS quiz cogs — lives in **`ai_tutor/`**; default API **port 5000** (configure via `PORT` env var to avoid conflict with lessons_lan).

```
.
├── server.js               # Node.js Mastery server (port 3000)
├── app.html                # Mastery frontend SPA
├── quiz-engine.js          # Auto-generated quiz questions
├── tests/
│   ├── quiz-engine.test.js # Node quiz engine tests
│   └── test_ai_tutor_api.py # AI tutor API contract tests
├── ai_tutor/               # Python AI tutor backend (merged from ProfessorSama)
│   ├── api.py              #   Flask API: /ask, /explain, /health
│   ├── tutor.py            #   Ollama AI explanation engine
│   ├── bot.py              #   Discord bot entry point
│   ├── questions.py        #   TEKS question bank
│   ├── progress.py         #   Per-user progress tracker
│   ├── .env.example        #   Environment variable template
│   └── cogs/               #   Discord command modules
│       ├── quiz.py         #     !quiz, !drill, !question
│       ├── homework.py     #     !ask, !solve
│       ├── progress.py     #     !progress, !xp, !weakskills
│       └── help_cmd.py     #     !help
├── lessons_lan/            # Python / Flask LAN app
│   ├── run.py
│   ├── main.py
│   ├── app/
│   └── README.md
├── requirements.txt        # Unified Python deps (all Python apps)
└── README.md
```

### Mastery (Node)

See [Setup](#-setup) above.

### Homeschool Lessons (Flask)

```powershell
cd lessons_lan
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5000` on this PC, or `http://<your-LAN-ip>:5000` on phones/tablets. More detail: [lessons_lan/README.md](lessons_lan/README.md).

### AI Tutor API (Flask)

```powershell
pip install -r requirements.txt
python -m ai_tutor.api
```

The API serves `POST /ask` (free-form homework help), `POST /explain` (structured quiz explanations), and `GET /health`. Requires a running Ollama instance for AI responses. See `ai_tutor/.env.example` for configuration.

### Discord Bot

```powershell
pip install -r requirements.txt
python -m ai_tutor.bot
```

Requires a Discord bot token in `.env`. Commands: `!quiz`, `!drill`, `!ask`, `!solve`, `!progress`, `!xp`, `!weakskills`, `!help`.

---

## 🔮 Next Evolutions

* Adaptive quiz generation
* AI-driven gap prioritization
* Cross-device cloud sync
* Parent insights (weakness trends)
* Voice-based interaction

---

## 🏁 End State

A system where:

* Learning is **targeted, not generalized**
* Progress is **visible and motivating**
* Weaknesses are **systematically eliminated**
* Education becomes **optimized like a feedback system**

---

## 🧭 Status

✅ Real-time system operational
✅ Gamification active
✅ Diagnostic loop functional
🟡 Adaptive intelligence (next phase)

## 🗺️ Product Phase + Roadmap

### Current Phase (as of April 6, 2026)
**Phase 2 — SSOT-driven diagnostics stabilization**

In this phase, the system treats the TEKS skills list as the single source of truth (SSOT) and ensures quiz availability tracks directly to that model.

### Roadmap

1. **Phase 1 (Completed): Core loop online**
   - Role-based login + dashboards
   - Skill lifecycle tracking (`unseen → needs_work → mastered`)
   - XP/levels/badges + real-time sync

2. **Phase 2 (Current): SSOT enforcement**
   - Auto-generated quizzes from skill records
   - Manual quiz override support for curated items
   - Domain-shape checks for quiz outputs

3. **Phase 3 (Next): Adaptive diagnostics**
   - Difficulty ramp based on quiz history
   - Gap-prioritized sequencing
   - Subject/strand-level weakness trend tracking

4. **Phase 4 (Later): Insight + planning**
   - Parent/teacher intervention recommendations
   - Progress forecasts and weekly plans
   - Optional cloud sync / multi-home support

<!-- DREAMVAULT_PORTFOLIO_README:BEGIN schema=v1 generated="2026-06-29T02:03:16Z" -->
## Portfolio status

**Homeschool + kids planner** — Family learning curriculum tied to weareswarm.online/kids-planner missions and rewards.

| Field | Value |
|---|---|
| **Canonical ID** | `HomeSchool_Mastery` |
| **Bucket** | unclassified |
| **Action** | — |
| **GitHub** | [HomeSchool_Mastery](https://github.com/Victor-Dixon/HomeSchool_Mastery) |

### Repository inventory

*Filesystem scan at `2026-06-29T02:03:16Z` — regenerate via `python runtime/scripts/sync_portfolio_readmes_001.py`.*

| Signal | Value |
|---|---|
| Python files | 53 |
| Test files | 1 |
| CI workflows | 0 |
| runtime/tasks YAML | 0 |
| pyproject.toml | no |
| package.json | no |
| tests/ directory | yes |
| Git branch | master |
| Working tree | dirty |

**Top-level directories:** .benchmarks, ai_tutor, docs, lessons_lan, runtime, tests

**Top-level files:** .gitignore, AGENTS.md, CONSOLIDATION_MANIFEST.md, MASTER_TASK_LIST.md, MASTER_TASK_LOG.md, NEXT_UP.md, PRD.md, PRODUCTION_READINESS.md, PROJECT_STRUCTURE_TREE.md, README.md, ROADMAP.md, ai_tutor_launcher.py, app.html, quiz-engine.js, requirements.txt, server.js

### Consolidation signals

- No pyproject.toml or package.json — packaging boundary unclear.
- No GitHub Actions workflows detected — CI gap.

### Run / verify

- `pip install -r requirements.txt`
<!-- DREAMVAULT_PORTFOLIO_README:END schema=v1 generated="2026-06-29T02:03:16Z" -->
