# Domain Model - HomeSchool Mastery

> Last updated: 2026-07-03

## What this project is

HomeSchool Mastery is a local-first family homeschool learning platform. The
current canonical product is the Flask LAN app in `lessons_lan/`. It serves
student lessons, practice, learning games, RPG-style accountability, and
parent/admin workflows from a household computer to devices on the home network.

## Why it exists

The project exists to make daily homeschool work visible and accountable:
students can see and complete today's work, practice TEKS/STAAR-aligned skills,
earn XP, face mastery gates, and receive feedback while a parent/admin can
manage lessons, reset passwords, and review student feedback.

## Domain

Primary domain: family homeschool education and learner accountability.

Implementation domain: local Flask/Jinja/SQLite web app for LAN use, with
optional local Ollama integration for AI coaching.

Curriculum domain: TEKS/STAAR-aligned Math and Reading/ELAR practice. The full
TEKS import pipeline and complete TEKS corpus are Unknown in the current repo;
the canonical app contains seeded standards, TEKS-tagged questions, and tests
around the current behavior.

## Bounded contexts

| Context | Location | Status | Purpose |
|---|---|---|---|
| Homeschool Lessons LAN app | `lessons_lan/` | Canonical | Daily lessons, practice, games, XP, boss fights, gear, feedback, admin |
| Node mastery prototype | repo root (`server.js`, `app.html`, `quiz-engine.js`) | Present but not canonical | Skill quiz prototype with local `data.json` persistence if run |
| AI tutor support package | `ai_tutor/` | Present support package | Flask `/ask` and `/explain` API, Discord bot, Ollama-backed tutoring, JSON progress |
| Documentation/governance | root docs, `docs/`, `runtime/tasks/` | Active | Product requirements, roadmap, task list, task log, agent rules |

Do not treat Node or `ai_tutor/` behavior as canonical `lessons_lan/` behavior
unless a document or implementation explicitly wires it into `lessons_lan/`.

## Core subdomains

| Subdomain | Canonical features | Primary modules/data |
|---|---|---|
| Lesson delivery | Today checklist, lesson detail pages, completion toggle | `lessons_lan/app/routes.py`, `lessons` and `completions` tables |
| Practice and mastery evidence | Practice quiz, snake practice, boss question attempts, mastery gates | `questions`, `question_attempts`, `boss_attempts`, `app/mastery.py`, `app/grading.py` |
| RPG/accountability | XP, level, Adventure page, milestone gates, boss fights | `player_state`, `app/rpg.py`, `app/routes.py` |
| Rewards | Boss loot rolls, gear catalog, per-student unlocks | `gear`, `gear_unlocks`, `app/loot.py` |
| Learning games | Text Detective, Discount Dash, Fraction Battle, Story Duel, Spelling Lab, Vocabulary Signal Breaker | game modules, JSON story bundles, Flask session |
| Parent/admin operations | Admin home, user password reset, lesson CRUD, feedback inbox | `app/auth.py`, admin routes, `feedback` table |
| AI coaching | Lesson AI coach and Story Duel grading through local Ollama, with fallbacks | `app/tutor.py`, `app/story_duel_llm.py`, environment variables |
| Content generation | Daily lesson plugin hook and emergency lessons; adaptive generator is tested but not routed | `app/plugin_loader.py`, `plugins/teks_daily_training/`, `app/generator.py` |

## Major entities

### Canonical persisted entities (`lessons_lan` SQLite)

Schema source: `lessons_lan/app/db.py`.

| Entity | Table | Key fields | Domain role | Current status |
|---|---|---|---|---|
| User | `users` | `id`, `username`, `display_name`, `grade`, `is_admin`, `password_hash` | Student or admin account | Active |
| Lesson | `lessons` | `user_id`, `lesson_date`, `subject`, `title`, `notes`, `sort_order` | Assigned learning unit | Active |
| Completion | `completions` | `lesson_id`, `completed_at` | Lesson done/undone marker | Active |
| Standard | `standards` | `framework`, `code`, `subject`, `grade`, `description` | TEKS-like standard catalog | Seeded placeholders; full import Unknown |
| LessonStandard | `lesson_standards` | `lesson_id`, `standard_id` | Lesson-to-standard mapping | Schema exists; active writes not found |
| Question | `questions` | `question_key`, `subject`, `grade`, `teks_tag`, `skill`, `item_type`, `choices_json`, `answer_key` | Practice/boss item bank | Active |
| QuestionAttempt | `question_attempts` | `user_id`, `question_id`, `is_correct`, `session_id` | Evidence for practice/mastery | Active |
| BossAttempt | `boss_attempts` | `user_id`, `boss_level`, `subject`, `score`, `max_score`, `passed`, `session_id` | Milestone assessment record | Active |
| Assessment | `assessments` | `user_id`, `subject`, `score`, `max_score`, `notes` | Score summary, currently boss-driven | Active |
| PlayerState | `player_state` | `user_id`, `xp`, `level`, `title`, `story_state_json` | XP and level state | XP/level active; title/story fields Unknown |
| Gear | `gear` | `gear_key`, `name`, `slot`, `rarity`, `power` | Reward catalog | Active |
| GearUnlock | `gear_unlocks` | `user_id`, `gear_id`, `source`, `unlocked_at` | Student reward ownership | Active |
| Badge | `badges` | `badge_key`, `name`, `criteria_json` | Achievement definition | Seeded; award logic Unknown |
| BadgeAward | `badge_awards` | `user_id`, `badge_id`, `awarded_at` | Student badge ownership | Schema exists; active writes not found |
| Feedback | `feedback` | `user_id`, `rating`, `message`, `context_json` | Student-to-admin feedback | Active |

### In-memory, session, and file-backed entities

| Entity | Store | Role |
|---|---|---|
| Flask session | signed cookie/session | Login state, mini-game state, lesson AI chat history, one-time XP guards |
| StoryDuelBundle | `lessons_lan/app/data/story_duel/*.json` | Swappable story/vocabulary duel content |
| DuelState/DuelToken | signed token via `itsdangerous` | Story Duel battle state passed between browser and server |
| TextDetectiveState | Flask session | Reading case battle state and XP bank |
| DiscountDashState | Flask session | Percent discount game state and XP bank |
| SpellingLabState | Flask session | Spelling practice state; no canonical XP write found |
| Vocabulary word bank | `lessons_lan/vocabulary_game.py` | Vocabulary Signal Breaker and CLI/GUI vocabulary data |
| Optional custom spelling words | `spelling_custom_words.txt` | Extra words if the file exists |

### Support-package entities (`ai_tutor/`)

These are not part of the canonical `lessons_lan` SQLite model.

| Entity | Store/module | Role |
|---|---|---|
| Tutor API request | `ai_tutor/api.py` | `/ask` and `/explain` JSON requests |
| Discord quiz session | `ai_tutor/cogs/quiz.py` | Active Discord command session |
| Tutor progress record | `ai_tutor/progress.py`, `data/progress.json` | Per-Discord-user skill stats and XP |
| Tutor question | `ai_tutor/questions.py` | TEKS-aligned support question bank |

### Node prototype entities

These are present in root files but are not the canonical app.

| Entity | Store/module | Role |
|---|---|---|
| Node user | `server.js` | Hard-coded student/teacher accounts |
| Skill record | `server.js`, `quiz-engine.js` | Skill definitions used to generate quizzes |
| Node quiz result | `data.json` when Node app runs | Prototype persistence; file is not committed in current inventory |

## Value objects

| Value object | Meaning | Evidence/status |
|---|---|---|
| TEKS tag | A curriculum alignment label on questions, for example `6.7A` | Active on `questions.teks_tag` |
| Skill | A question-bank skill label such as `main_idea` or `percent_discount` | Active on `questions.skill` |
| Subject | Lesson/question grouping such as Math or Reading/ELAR | Active |
| Grade | Student grade and question grade filter | Active |
| XP | Non-negative progress points | Active in `player_state.xp`; XP is added, not deducted |
| Level | Derived/stored progression level | Active in `player_state.level` |
| Session ID | UUID grouping of attempts | Active on question and boss attempts |
| Game marker | Lesson note marker such as `game:text-detective` or `game:discount-dash` | Active lesson routing convention |
| Story bundle slug | Marker such as `story_duel_bundle:<slug>` | Active content override convention |
| Boss milestone | Level gate at 10, 20, 30, ... | Active in RPG logic |
| Mastery thresholds | 85% accuracy, mixed review count, 80% boss score | Active in `app/mastery.py` tests |
| Loot rarity | Gear rarity tier | Active in `app/loot.py` |
| Duel token | Signed opaque Story Duel state | Active |

## Services and modules

| Service/module | Responsibility |
|---|---|
| `lessons_lan/app/__init__.py` | Flask app factory, DB init, blueprint registration, plugin loading |
| `lessons_lan/run.py`, `main.py` | Server entrypoint; Waitress by default, Flask dev server with env flag |
| `lessons_lan/app/db.py` | SQLite connection, schema, seed data, reset/init CLI |
| `lessons_lan/app/auth.py` | Session login, `login_required`, `admin_required` |
| `lessons_lan/app/routes.py` | Main student, lesson, practice, game, feedback, admin, boss routes |
| `lessons_lan/app/rpg.py` | XP, level, gate snapshots, boss level helpers |
| `lessons_lan/app/mastery.py` | Pure mastery gate rules |
| `lessons_lan/app/grading.py` | Item-type grading |
| `lessons_lan/app/loot.py` | Score-weighted gear drops |
| `lessons_lan/app/generator.py` | Adaptive lesson picker; tested but not routed in current app |
| `lessons_lan/app/plugin_loader.py` | Plugin manifest loading and hook dispatch |
| `lessons_lan/plugins/teks_daily_training/plugin.py` | Daily lesson generation hook |
| `lessons_lan/app/tutor.py` | Optional Ollama lesson coach wrapper |
| `lessons_lan/app/story_duel*.py` | Story Duel bundles, grading, token state, schema |
| `lessons_lan/app/text_detective.py` | Text Detective game logic |
| `lessons_lan/app/discount_dash.py` | Discount Dash game logic |
| `lessons_lan/app/spelling_lab_routes.py` | Web Spelling Lab API |
| `lessons_lan/app/vocab_signal_routes.py` | Vocabulary Signal Breaker page |
| `ai_tutor/*` | Separate Ollama API/Discord tutor support package |
| `server.js`, `quiz-engine.js` | Separate Node prototype runtime and quiz generator |

## Relationships

```text
User 1--many Lesson
Lesson 1--0/1 Completion
User 1--1 PlayerState
User 1--many QuestionAttempt
Question 1--many QuestionAttempt
User 1--many BossAttempt
User 1--many Assessment
User 1--many GearUnlock
Gear 1--many GearUnlock
User 1--many Feedback
Lesson many--many Standard through LessonStandard (schema present; current writes Unknown)
User many--many Badge through BadgeAward (schema present; current writes Unknown)
```

## Data flow

### Daily lesson flow

1. Student logs in through `/login`.
2. `/today` loads the student's lessons for the current date.
3. If no lessons exist, the app asks plugins for daily lessons and falls back to
   emergency seed lessons if needed.
4. Student opens a lesson, completes work, and toggles completion.
5. Completion can award XP through `add_xp`.

### Practice/mastery flow

1. Student opens practice or snake practice from a lesson.
2. The app selects questions by subject/grade and records attempts.
3. Correct answers add XP.
4. Mastery gates use recent attempt accuracy, mixed review evidence, and boss
   score thresholds to cap milestone level progression.

### Boss/reward flow

1. Student opens the Adventure page and then a boss fight.
2. Boss questions are graded and saved as question attempts.
3. The app records a boss attempt and assessment.
4. Passing can award bonus XP and gear through a loot roll.

### Game flow

Text Detective, Discount Dash, Fraction Battle, Story Duel, Spelling Lab, and
Vocabulary Signal Breaker are learning games attached to lesson or games-hub
routes. Some games award XP (`Text Detective`, `Discount Dash`, `Fraction
Battle`, `Story Duel`); Spelling Lab and Vocabulary Signal Breaker are currently
documented as practice/games without canonical persisted XP writes.

### Parent/admin flow

Admin users can list users, reset passwords, add/edit/delete lessons, and read
feedback. Student routes and admin routes are separated by `login_required` and
`admin_required`.

## User interactions

| Actor | Interactions |
|---|---|
| Student | Login, view Today, open lessons, toggle completion, practice, play learning games, submit feedback, view Adventure and boss fights |
| Parent/Admin | Login, manage lessons, reset passwords, review feedback, operate local app |
| Operator | Start/stop LAN server, manage SQLite database, run tests, perform backups |

## External integrations

| Integration | Used by | Status |
|---|---|---|
| SQLite | `lessons_lan` | Primary local persistence |
| Waitress | `lessons_lan/run.py` | Default production-style WSGI server |
| Ollama HTTP API | lesson AI coach, Story Duel grading, `ai_tutor` | Optional local integration with fallback/offline behavior |
| Discord | `ai_tutor` bot | Present support package; not canonical `lessons_lan` dependency |
| Windows Startup/Scheduled Task scripts | `lessons_lan/autostart/` | Operator convenience |

No evidence was found for a cloud database, OAuth, email delivery, or deployed
third-party LMS integration.

## Feature-to-domain mapping

| Feature | Domain entities/subdomains |
|---|---|
| Today checklist | User, Lesson, Completion, Lesson delivery |
| Lesson detail | Lesson, game marker value objects |
| Lesson AI coach | Lesson, AI coaching, Flask session, Ollama |
| Practice quiz | Question, QuestionAttempt, PlayerState, Practice/mastery |
| Snake practice | Question, QuestionAttempt, PlayerState |
| Fraction Battle | Lesson, PlayerState, Game flow |
| Text Detective | Lesson, TextDetectiveState, PlayerState |
| Discount Dash | Lesson, DiscountDashState, PlayerState |
| Story Duel | StoryDuelBundle, DuelState, DuelToken, PlayerState, Ollama/heuristic grading |
| Spelling Lab | SpellingLabState, vocabulary/spelling word data |
| Vocabulary Signal Breaker | Vocabulary word bank |
| Adventure page | PlayerState, mastery gate snapshot, Boss milestone |
| Boss fight | Question, QuestionAttempt, BossAttempt, Assessment, PlayerState |
| Gear/loot | Gear, GearUnlock, loot service |
| Feedback | Feedback, User, admin review |
| Admin lesson management | User, Lesson, admin operations |
| Password reset | User, admin operations |
| Daily lesson plugin | Lesson, plugin LessonItem, content generation |
| AI tutor package | Tutor API request, Discord session, tutor progress record |
| Node quiz prototype | Node user, skill record, node quiz result |

## Repository audit findings

### Architecture

- Canonical implementation: `lessons_lan/`, a Flask app with Jinja templates,
  SQLite, and Waitress.
- Additional runtimes exist: a root Node prototype and an `ai_tutor/` Flask/API
  plus Discord package.
- The runtimes do not share a single database in the current repository.

### Folder structure

- `lessons_lan/`: canonical app, tests, templates, static assets, plugins,
  local data bundles, autostart scripts.
- `ai_tutor/`: support package for Ollama API and Discord commands.
- repo root: Node prototype files and governance docs.
- `docs/`: product/domain/roadmap documentation.
- `runtime/tasks/`: expanded task list and task log.
- `tests/`: root tests for Node quiz engine and `ai_tutor` API.

### Documentation state after this audit

- Canonical documentation entrypoint: `docs/README.md`.
- Product requirements: root `PRD.md` summary plus expanded `docs/PRD.md`.
- Roadmap: root `ROADMAP.md` summary plus expanded `docs/ROADMAP.md`.
- Task tracking: root task docs summarize and point to expanded
  `runtime/tasks/` docs.
- App operations: `lessons_lan/README.md` and `lessons_lan/PASSDOWN.md`.

### Naming decisions

- Product name: "HomeSchool Mastery" in prose; repository name remains
  `HomeSchool_Mastery`.
- Canonical app name: "Homeschool Lessons LAN app" or `lessons_lan/`.
- Operator role: "Parent/Admin" for the canonical app. "Teacher" appears in
  older Node docs and means the same household oversight role when discussing
  legacy/prototype behavior.

## Unknowns and inactive schema

Unknown means no current repository evidence proves the behavior.

| Item | Status |
|---|---|
| Complete TEKS corpus import and coverage | Unknown |
| Full standard-to-lesson mapping writes | Unknown; schema exists |
| Badge award business rules | Unknown; badge schema exists |
| Intended use of `player_state.title` and `story_state_json` | Unknown |
| Whether Node prototype is actively operated in the household | Unknown |
| Whether `ai_tutor` Discord bot is currently deployed | Unknown |
| Cross-runtime data synchronization | Unknown; no shared store found |
| Backup/export implementation for `lessons_lan` learner data | Unknown/open |
| CI workflow for current tests | Unknown/open; no workflow found |

## Invariants for future changes

1. Preserve learner safety and parent/admin route separation.
2. Keep the app local-first unless a future document explicitly changes scope.
3. Do not delete generated databases or student data during normal operation.
4. Treat destructive reset commands as operator-only maintenance actions.
5. Do not weaken XP, mastery gates, attempts, boss rewards, or accountability
   behavior without tests.
6. Mark unverified architecture and requirements as Unknown rather than
   documenting them as shipped behavior.
