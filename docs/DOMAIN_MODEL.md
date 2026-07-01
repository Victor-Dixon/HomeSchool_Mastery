# Domain Model — HomeSchool Mastery

> Last updated: 2026-05-25

This document defines the core domain entities, their attributes, and relationships within the HomeSchool Mastery system.

---

## Entity Overview

```
Student ──takes──▶ Quiz ──covers──▶ Skill ──belongs to──▶ Subject
   │                                  │
   │                                  ├── aligned to ──▶ TEKS Standard
   │                                  │
   ├── earns ──▶ XP ──unlocks──▶ Badge
   │
   ├── completes ──▶ Lesson
   │
   └── participates in ──▶ Session

Teacher ──monitors──▶ Student (all)
Teacher ──manages──▶ Quiz, Skill, Lesson
```

---

## Entities

### Student

A learner in the household with their own progress state.

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | Student's first name (Charlie, Chris) |
| grade | integer | Current grade level (6, 7) |
| pin | string | Login credential for role-based access |
| xp | integer | Accumulated experience points |
| level | integer | Current level (derived: XP ÷ 500) |
| badges | list[Badge] | Earned achievement badges |
| skills | map[Skill → Status] | Per-skill mastery state |

### Skill

A discrete learning objective aligned to TEKS standards.

| Attribute | Type | Description |
|-----------|------|-------------|
| id | string | Unique skill identifier |
| subject | Subject | Parent subject area |
| strand | string | TEKS strand within subject |
| description | string | Human-readable skill description |
| status | enum | `unseen` → `needs_work` → `mastered` |
| teks_code | string | TEKS standard reference code |

**Lifecycle:**

```
unseen ──(first quiz attempt)──▶ needs_work ──(pass quiz)──▶ mastered
                                      ▲                          │
                                      └──(fail subsequent quiz)──┘
```

A skill starts as `unseen`. The first interaction transitions it to `needs_work`. It becomes `mastered` only when the student passes the associated quiz. Mastery can regress if a subsequent diagnostic reveals loss of retention.

### Quiz

A short diagnostic assessment tied to a specific skill.

| Attribute | Type | Description |
|-----------|------|-------------|
| skill_ref | Skill | The skill being assessed |
| questions | list[Question] | 2–3 questions per quiz |
| answers | list[Answer] | Expected correct answers |
| pass_threshold | float | Minimum score to mark skill as mastered (typically 100%) |
| source | enum | `auto_generated` or `curated` (manual override) |

### Badge

An achievement reward for reaching milestones.

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | Badge title |
| criteria | string | Human-readable earn condition |
| xp_threshold | integer | Minimum XP required (where applicable) |
| icon | string | Display icon reference |

**Known Badges:**

| Badge | Criteria |
|-------|----------|
| First Win | Complete first quiz |
| On Fire | 3 quizzes in a row correct |
| Scholar | Master 10 skills |
| Legend | Master 50 skills |
| Math Wizard | Master all math skills |
| Word Master | Master all ELA skills |
| Perfectionist | 100% on 5 consecutive quizzes |
| Grinder | Complete 20 quizzes in one session |
| Comeback Kid | Master a skill after 3+ failed attempts |
| Unstoppable | Reach level 10 |

### Lesson

A structured learning unit in the Flask LAN app.

| Attribute | Type | Description |
|-----------|------|-------------|
| subject | Subject | Parent subject area |
| title | string | Lesson title |
| content | text | Teaching material |
| practice_items | list[Item] | Associated practice exercises |
| completion_status | enum | `not_started`, `in_progress`, `completed` |

### Subject

A top-level curriculum area aligned to TEKS standards.

| Subject | TEKS Grades | Strands (examples) |
|---------|-------------|---------------------|
| Math | 6th, 7th | Number & Operations, Algebraic Reasoning, Geometry |
| ELA | 6th, 7th | Reading, Writing, Vocabulary, Spelling |
| Science | 6th, 7th | Life Science, Earth Science, Physical Science |
| Social Studies | 6th, 7th | History, Geography, Government, Economics |

### Session

A daily learning workflow instance.

| Phase | Duration | Action |
|-------|----------|--------|
| Review | ~5 min | Open app, review current gaps |
| Teach | ~20 min | Focus instruction on weak skills |
| Quiz | ~5 min | Run diagnostics, update mastery state |
| Update | automatic | XP awarded, badges checked, dashboard refreshed |

### Teacher Dashboard

Victor's multi-student monitoring interface.

| Capability | Description |
|------------|-------------|
| Multi-student view | See both students' progress simultaneously |
| Subject progress | Track mastery percentage by subject and strand |
| Gap identification | Surface skills stuck in `needs_work` state |
| CSV export | Export progress data for external reporting |
| Quiz management | Override or curate quiz content |

### Data Layer

| Store | Technology | Purpose |
|-------|-----------|---------|
| data.json | JSON file | Node app persistence — skills, XP, badges, quiz results |
| SQLite / local DB | SQLite | Flask app persistence — lessons, practice, vocabulary |
| CSV export | Generated file | Teacher reporting output |

---

## Relationships Summary

| Relationship | Cardinality | Description |
|-------------|-------------|-------------|
| Student → Skill | many-to-many | Each student has their own status per skill |
| Student → Quiz | one-to-many | A student takes many quizzes over time |
| Quiz → Skill | many-to-one | Each quiz assesses exactly one skill |
| Skill → Subject | many-to-one | Skills are grouped under subjects |
| Student → Badge | one-to-many | A student earns badges as milestones are hit |
| Student → Lesson | one-to-many | A student completes lessons in the Flask app |
| Teacher → Student | one-to-many | Victor monitors all students |

---

## Invariants

1. **Skill status transitions are one-directional** (with regression only via failed re-assessment).
2. **Every quiz maps to exactly one skill** — no orphan quizzes.
3. **XP is monotonically increasing** — XP is never deducted.
4. **Badges are permanent** — once earned, a badge is never revoked.
5. **Student data is never deleted** — history is preserved for trend analysis.
6. **TEKS alignment is required** — every skill must reference a valid TEKS standard code.
