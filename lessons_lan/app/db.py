"""
Project: Homeschool Lessons (Dream.OS)
File: app/db.py
Purpose: SQLite database connection, schema, seed data, and init hooks.
Owner: Local family deployment (homeschool)
"""

import os
import sqlite3
from datetime import date

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash


def get_db():
    if "db" not in g:
        os.makedirs(current_app.instance_path, exist_ok=True)
        db_path = current_app.config.get("DATABASE") or os.path.join(current_app.instance_path, "homeschool.db")
        # timeout: share DB safely across Waitress threads; WAL: readers don't block as badly
        g.db = sqlite3.connect(db_path, timeout=30.0, check_same_thread=False)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
    return g.db


def close_db(_e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  display_name TEXT NOT NULL,
  grade INTEGER,
  is_admin INTEGER NOT NULL DEFAULT 0,
  password_hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS lessons (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  lesson_date TEXT NOT NULL,
  subject TEXT NOT NULL,
  title TEXT NOT NULL,
  notes TEXT,
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS completions (
  lesson_id INTEGER PRIMARY KEY,
  completed_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS standards (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  framework TEXT NOT NULL,            -- e.g. TEKS
  subject TEXT NOT NULL,              -- e.g. Math
  grade INTEGER,                      -- e.g. 6
  code TEXT NOT NULL,                 -- e.g. "111.26.b.2"
  description TEXT NOT NULL,
  url TEXT,
  UNIQUE(framework, code)
);

CREATE TABLE IF NOT EXISTS lesson_standards (
  lesson_id INTEGER NOT NULL,
  standard_id INTEGER NOT NULL,
  PRIMARY KEY (lesson_id, standard_id),
  FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
  FOREIGN KEY (standard_id) REFERENCES standards(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS assessments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  assessed_on TEXT NOT NULL,          -- ISO date
  subject TEXT NOT NULL,
  standard_id INTEGER,                -- optional: tie to a TEKS standard
  score REAL,                         -- raw score
  max_score REAL,                     -- max score
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (standard_id) REFERENCES standards(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS badges (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  badge_key TEXT UNIQUE NOT NULL,     -- stable ID for plugins
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  icon TEXT,                          -- optional (emoji or short text)
  criteria_json TEXT NOT NULL DEFAULT '{}',
  plugin TEXT,                        -- plugin name that owns this badge (optional)
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS badge_awards (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  badge_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  awarded_at TEXT NOT NULL DEFAULT (datetime('now')),
  evidence_json TEXT NOT NULL DEFAULT '{}',
  UNIQUE(badge_id, user_id),
  FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  rating INTEGER,                     -- 1-5 (optional)
  message TEXT NOT NULL,
  context_json TEXT NOT NULL DEFAULT '{}',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS player_state (
  user_id INTEGER PRIMARY KEY,
  xp INTEGER NOT NULL DEFAULT 0,
  level INTEGER NOT NULL DEFAULT 1,
  title TEXT NOT NULL DEFAULT '',
  story_state_json TEXT NOT NULL DEFAULT '{}',
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question_key TEXT UNIQUE NOT NULL,  -- stable ID
  subject TEXT NOT NULL,              -- Math / Reading (ELAR)
  grade INTEGER,                      -- 6,7 (or band)
  teks_tag TEXT NOT NULL,             -- e.g. 6.4H
  skill TEXT NOT NULL,                -- e.g. one_step_equations
  difficulty INTEGER NOT NULL DEFAULT 1, -- 1 easy, 2 med, 3 hard
  item_type TEXT NOT NULL DEFAULT 'multiple_choice',
  staar_style INTEGER NOT NULL DEFAULT 1,
  prompt TEXT NOT NULL,
  choices_json TEXT NOT NULL,         -- JSON array of strings
  answer_key TEXT NOT NULL,           -- e.g. "A" (or index as string)
  explanation TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS question_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  question_id INTEGER NOT NULL,
  attempted_at TEXT NOT NULL DEFAULT (datetime('now')),
  selected_key TEXT,
  is_correct INTEGER NOT NULL,
  session_id TEXT,                    -- tie attempts to a boss run
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS boss_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  boss_level INTEGER NOT NULL,         -- 10,20,30...
  subject TEXT NOT NULL,
  started_at TEXT NOT NULL DEFAULT (datetime('now')),
  finished_at TEXT,
  score REAL,
  max_score REAL,
  passed INTEGER NOT NULL DEFAULT 0,
  session_id TEXT UNIQUE NOT NULL,
  details_json TEXT NOT NULL DEFAULT '{}',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS gear (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  gear_key TEXT UNIQUE NOT NULL,       -- stable ID
  slot TEXT NOT NULL,                  -- helmet/chest/boots/weapon/shield/gauntlets
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  rarity TEXT NOT NULL DEFAULT 'common',
  icon TEXT NOT NULL DEFAULT '🧰',
  criteria_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS gear_unlocks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  gear_id INTEGER NOT NULL,
  unlocked_at TEXT NOT NULL DEFAULT (datetime('now')),
  reason TEXT NOT NULL DEFAULT '',
  UNIQUE(user_id, gear_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (gear_id) REFERENCES gear(id) ON DELETE CASCADE
);
"""


def init_db():
    db = get_db()
    db.executescript(SCHEMA_SQL)
    db.commit()


def insert_emergency_lessons(db, user_id: int, today_s: str, grade, username: str) -> int:
    """
    If a student has zero lessons for today (plugin failed, empty DB, etc.),
    insert short Math + Reading items that always match the built-in Practice question bank.
    """
    n = db.execute(
        "SELECT COUNT(*) AS c FROM lessons WHERE user_id = ? AND lesson_date = ?",
        (user_id, today_s),
    ).fetchone()["c"]
    if n > 0:
        return 0

    g = 0
    try:
        if grade is not None:
            g = int(grade)
    except (TypeError, ValueError):
        g = 0
    if g <= 0:
        u = (username or "").lower()
        if u == "charlie":
            g = 6
        elif u == "chris":
            g = 7
        else:
            g = 6

    if g <= 6:
        rows = [
            (
                user_id,
                today_s,
                "Math",
                "Grade 6 warm-up: fractions (play Practice)",
                "Goal: Add and subtract fractions with like denominators.\n\n"
                "Quick rule: same denominator — add or subtract the numerators only.\n\n"
                "Practice:\n"
                "1) 3/8 + 2/8 = ?\n"
                "2) 7/10 - 4/10 = ?\n\n"
                "Play: tap Practice on this lesson for multiple-choice + XP.\n\n"
                "Questions:\n"
                "Why do denominators have to match before you add?",
                1,
            ),
            (
                user_id,
                today_s,
                "Reading (ELAR)",
                "Grade 6: main idea + inference",
                "Goal: State the main idea and make a smart inference from clues.\n\n"
                "Passage:\n"
                "Marcus found a wallet on the ground. No one was around. He looked inside and saw money and an ID. "
                "He paused, then walked toward the office.\n\n"
                "Questions:\n"
                "1) What is the main idea?\n"
                "2) What can you infer Marcus is thinking?\n\n"
                "Practice:\n"
                "Write one main-idea sentence and one inference sentence with evidence.\n\n"
                "Play: Practice pits you against reading questions like this.",
                2,
            ),
        ]
    else:
        rows = [
            (
                user_id,
                today_s,
                "Reading (ELAR)",
                "Grade 7: purpose, structure, evidence (play Practice)",
                "Goal: Explain author’s purpose and back it with text evidence.\n\n"
                "Passage:\n"
                "The author describes a storm as “angry and alive,” shaking the town with force.\n\n"
                "Questions:\n"
                "1) What is the author’s purpose in that description?\n"
                "2) What evidence shows strong mood?\n\n"
                "Practice:\n"
                "Two sentences: purpose + one quote as proof.\n\n"
                "Play: open Practice for grade 7 reading quiz + XP.",
                1,
            ),
            (
                user_id,
                today_s,
                "Math",
                "Grade 7: percent + two-step equations",
                "Goal: Handle a percent discount and a two-step equation (same items as Practice).\n\n"
                "Practice:\n"
                "1) Shirt $20, 25% off — what is the sale price?\n"
                "2) Solve: 2x + 5 = 15 (show steps).\n\n"
                "Play: Practice runs the game version for XP.\n\n"
                "Questions:\n"
                "Which do you prefer — subtract the discount or pay the remaining percent of the price?",
                2,
            ),
        ]

    db.executemany(
        "INSERT INTO lessons (user_id, lesson_date, subject, title, notes, sort_order) VALUES (?,?,?,?,?,?)",
        rows,
    )
    db.commit()
    return len(rows)


def seed_if_empty():
    db = get_db()
    user_count = db.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    if user_count > 0:
        return

    # Student passwords match scripts/set_passwords.py (home LAN — change if exposed).
    users = [
        ("admin", "Admin", None, 1, "admin123"),
        ("charlie", "Charlie", 6, 0, "34086028"),
        ("chris", "Chris", 7, 0, "0822"),
    ]
    for username, display_name, grade, is_admin, pw in users:
        db.execute(
            "INSERT INTO users (username, display_name, grade, is_admin, password_hash) VALUES (?,?,?,?,?)",
            (username, display_name, grade, is_admin, generate_password_hash(pw)),
        )

    db.commit()

    # Add a couple of example lessons for today (must include full details payload).
    today = date.today().isoformat()
    charlie_id = db.execute("SELECT id FROM users WHERE username='charlie'").fetchone()["id"]
    chris_id = db.execute("SELECT id FROM users WHERE username='chris'").fetchone()["id"]

    examples = [
        (
            charlie_id,
            today,
            "Math",
            "Grade 6: fractions boost — play Practice",
            "Goal: Add and subtract fractions with like denominators.\n\n"
            "Quick rule:\n"
            "- Same denominator → keep it, add/subtract numerators.\n\n"
            "Guided example:\n"
            "1/5 + 2/5 = 3/5\n\n"
            "Practice:\n"
            "1) 3/8 + 2/8 = ?\n"
            "2) 7/10 - 4/10 = ?\n\n"
            "Play: tap Practice on this lesson for timed quiz + XP.\n\n"
            "Challenge:\n"
            "5/6 - 2/6 + 1/6 = ?\n\n"
            "Questions:\n"
            "Why do denominators need to match?",
            1,
        ),
        (
            charlie_id,
            today,
            "Reading (ELAR)",
            "Grade 6: main idea + inference (play Practice)",
            "Goal: Use text clues to infer and state the main idea.\n\n"
            "Passage:\n"
            "Marcus found a wallet on the ground. No one was around. He looked inside and saw money and an ID. "
            "He paused, then walked toward the office.\n\n"
            "Questions:\n"
            "1) What is the main idea?\n"
            "2) What can you infer Marcus is thinking?\n"
            "3) What is a possible theme?\n\n"
            "Practice:\n"
            "Write 2 sentences: one main idea sentence + one inference sentence with evidence.\n\n"
            "Play: Practice uses reading questions at your level for XP.",
            2,
        ),
        (
            chris_id,
            today,
            "Reading (ELAR)",
            "Author purpose + text structure + evidence",
            "game:text-detective\n\n"
            "Goal: Read like a detective — purpose, structure, and proof.\n\n"
            "Passage:\n"
            "The author describes a storm as “angry and alive,” shaking the town with force.\n\n"
            "Questions:\n"
            "1) What is the author’s purpose for this description?\n"
            "2) What text structure are you noticing?\n"
            "3) What evidence supports your answer?\n\n"
            "Practice:\n"
            "Tap Practice (on this lesson) to play quiz questions tied to this skill, then summarize in two sentences.\n\n"
            "Reflection:\n"
            "How did vivid verbs and adjectives change the mood?",
            1,
        ),
        (
            chris_id,
            today,
            "Math",
            "Percent discount (real world)",
            "game:discount-dash\n\n"
            "Goal: Apply a percent discount — same skill as the Practice quiz.\n\n"
            "Problem:\n"
            "A shirt costs $20. It’s 25% off. What is the sale price?\n\n"
            "Steps:\n"
            "1) Find 25% of $20.\n"
            "2) Subtract from $20 — or pay 75% of $20.\n\n"
            "Practice:\n"
            "Open **Practice** for timed multiple-choice on this skill.\n\n"
            "Challenge:\n"
            "Explain which method you like: subtract the discount, or multiply by (100% − 25%).",
            2,
        ),
        (
            chris_id,
            today,
            "Math",
            "Two-step equations",
            "Goal: Isolate x when two operations are in the way.\n\n"
            "Example: 2x + 5 = 15 → subtract 5 → 2x = 10 → x = 5.\n\n"
            "Practice:\n"
            "Use Practice for quiz items, then show work for: 3x − 4 = 14.\n\n"
            "Reflection:\n"
            "Why do we undo addition before multiplication in this flow?",
            3,
        ),
    ]
    db.executemany(
        "INSERT INTO lessons (user_id, lesson_date, subject, title, notes, sort_order) VALUES (?,?,?,?,?,?)",
        examples,
    )
    db.commit()

    # Seed a couple of sample TEKS-like standards + a starter badge (placeholders until you import full TEKS).
    standards = [
        ("TEKS", "Math", 6, "TEKS-M6-EX1", "Fractions: represent and compare fractions.", ""),
        ("TEKS", "ELA", 6, "TEKS-ELA6-EX1", "Reading: demonstrate understanding of texts.", ""),
        ("TEKS", "Science", 7, "TEKS-SCI7-EX1", "Cells: describe basic cell functions.", ""),
    ]
    db.executemany(
        "INSERT OR IGNORE INTO standards (framework, subject, grade, code, description, url) VALUES (?,?,?,?,?,?)",
        standards,
    )

    db.execute(
        "INSERT OR IGNORE INTO badges (badge_key, name, description, icon, criteria_json, plugin) VALUES (?,?,?,?,?,?)",
        ("starter_streak_1", "First Win", "Completed your first lesson item.", "🏁", '{"type":"first_completion"}', "core"),
    )

    # Seed a few sample questions (placeholder question bank; you can expand/import later).
    # Reading (Grade 6): main idea/inference/theme
    q = [
        (
            "r6_main_idea_001",
            "Reading (ELAR)",
            6,
            "6.R.1",
            "main_idea",
            1,
            "Marcus found a wallet on the ground. No one was around. He looked inside and saw money and an ID. He paused, then walked toward the office.\n\nWhat is the main idea?",
            '["Marcus is late to class.","Marcus finds a wallet and decides what to do.","Marcus loses his ID.","Marcus buys something with the money."]',
            "B",
        ),
        (
            "r6_infer_001",
            "Reading (ELAR)",
            6,
            "6.R.2",
            "inference",
            2,
            "Marcus found a wallet with an ID and money, then walked toward the office.\n\nWhat can you infer Marcus is most likely thinking?",
            '["I should keep this because no one saw me.","I should return this to the owner.","I should throw it away.","I should hide it in my bag."]',
            "B",
        ),
        # Math (Grade 6): one-step equation
        (
            "m6_eq_001",
            "Math",
            6,
            "6.7A",
            "one_step_equations",
            1,
            "Solve: x + 7 = 15",
            '["x = 6","x = 7","x = 8","x = 22"]',
            "C",
        ),
        # Reading (Grade 7): author purpose
        (
            "r7_author_001",
            "Reading (ELAR)",
            7,
            "7.R.6",
            "author_purpose",
            2,
            "The author describes a storm as “angry and alive,” shaking the town with force.\n\nWhat is the author’s purpose for using this description?",
            '["To list facts about weather","To persuade readers to buy storm supplies","To create a vivid mood and imagery","To explain how storms form scientifically"]',
            "C",
        ),
        (
            "r7_text_structure_001",
            "Reading (ELAR)",
            7,
            "7.R.7",
            "text_structure",
            2,
            "A passage compares two types of energy sources by listing how they are similar and different.\n\nWhich text structure is used?",
            '["Cause and effect","Compare and contrast","Chronological order","Problem and solution"]',
            "B",
        ),
        (
            "r7_evidence_001",
            "Reading (ELAR)",
            7,
            "7.R.3",
            "text_evidence",
            2,
            "Which choice is the best evidence that the character is nervous?\n\n(Imagine the text says the character’s hands were shaking and they kept looking at the door.)",
            '["The character walked home.","The character’s hands were shaking and they kept looking at the door.","The character smiled at a friend.","The character ate lunch quickly."]',
            "B",
        ),
        # Math (Grade 7): percent discount
        (
            "m7_percent_001",
            "Math",
            7,
            "7.3B",
            "percent_discount",
            1,
            "A shirt costs $20. It’s 25% off. What is the new price?",
            '["$5","$10","$15","$25"]',
            "C",
        ),
        # Math (Grade 7): two-step equation
        (
            "m7_eq_001",
            "Math",
            7,
            "7.10A",
            "two_step_equations",
            2,
            "Solve: 2x + 5 = 15",
            '["x = 3","x = 5","x = 10","x = 20"]',
            "B",
        ),
    ]
    db.executemany(
        """
        INSERT OR IGNORE INTO questions
          (question_key, subject, grade, teks_tag, skill, difficulty, prompt, choices_json, answer_key)
        VALUES (?,?,?,?,?,?,?,?,?)
        """,
        q,
    )

    # Seed starter gear
    gear_rows = [
        ("starter_wood_sword", "weapon", "Wooden Sword", "Earned by starting your journey.", "common", "🗡️", '{"type":"starter"}'),
        ("reading_dragon_scale", "chest", "Dragon Scale Vest", "Awarded for clearing the Reading Dragon (Level 10 boss).", "rare", "🐉", '{"type":"boss_clear","boss_level":10,"subject":"Reading (ELAR)"}'),
        ("blade_perfect_score", "weapon", "Blade of the Perfect Score", "Higher chance when you ace boss fights.", "legendary", "⚔️", '{"type":"perfect_score"}'),
    ]
    db.executemany(
        """
        INSERT OR IGNORE INTO gear (gear_key, slot, name, description, rarity, icon, criteria_json)
        VALUES (?,?,?,?,?,?,?)
        """,
        gear_rows,
    )
    db.commit()


@click.command("init-db")
@with_appcontext
def init_db_command():
    init_db()
    seed_if_empty()
    click.echo("Initialized the database.")


def _database_path() -> str:
    instance = current_app.instance_path
    os.makedirs(instance, exist_ok=True)
    return current_app.config.get("DATABASE") or os.path.join(instance, "homeschool.db")


@click.command("reset-db")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation (for scripts).")
@with_appcontext
def reset_db_command(yes: bool):
    """
    Delete the SQLite file and re-run schema + seed. Stop the server first if you get 'file in use'.
    """
    db_path = _database_path()
    if not yes and not click.confirm(f"Delete ALL data and reseed?\n  {db_path}"):
        click.echo("Cancelled.")
        return
    close_db()
    try:
        if os.path.isfile(db_path):
            os.remove(db_path)
    except PermissionError as exc:
        click.echo(
            f"Could not remove database (is the app still running?). Close Waitress/Flask, then retry.\n{exc}",
            err=True,
        )
        raise SystemExit(1) from exc
    init_db()
    seed_if_empty()
    click.echo(f"Reset complete: {db_path}")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(reset_db_command)

    with app.app_context():
        init_db()
        seed_if_empty()

