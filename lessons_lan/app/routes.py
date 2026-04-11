"""
Project: Homeschool Lessons (Dream.OS)
File: app/routes.py
Purpose: Web routes (Today, Lessons, Practice/Snake, Admin, Feedback, Adventure, Boss fights).
Owner: Local family deployment (homeschool)
"""

import json
import os
import random
from datetime import date
from uuid import uuid4

from flask import Blueprint, flash, g, jsonify, redirect, render_template, request, session, url_for, current_app
from werkzeug.security import generate_password_hash

from .auth import admin_required, load_logged_in_user, login, login_required, logout
from .db import get_db
from .plugin_loader import call_first
from .tutor import build_lesson_system_prompt, ollama_chat
from .loot import roll_gear
from .mastery import can_level_up
from .grading import grade_mcq, grade_mcq_choice_text, grade_multi_select, grade_ordering, grade_short_response, normalize_text
from .rpg import (
    add_xp,
    build_student_gate_snapshot,
    ensure_player_state,
    get_next_boss_level,
    pick_boss_subject,
    snake_opponent_for_lesson,
    snake_question_subject_for_lesson,
)
from .story_duel import (
    apply_round,
    coerce_duel_state,
    decode_duel_state,
    encode_duel_state,
    initial_state,
    serialize_bundle_public,
    xp_for_outcome,
)
from .story_duel_loader import bundle_id_from_lesson_notes, get_default_bundle_id, load_story_bundle
from .text_detective import (
    detective_client_bundle,
    detective_get_state,
    detective_set_state,
    process_reflection as td_process_reflection,
    process_step as td_process_step,
    public_bundle as td_public_bundle,
    session_key as td_session_key,
    td_initial_state,
)
from .discount_dash import (
    get_dash_state,
    initial_state as dd_initial_state,
    process_answer as dd_process_answer,
    process_method_bonus as dd_process_method_bonus,
    public_intro as dd_public_intro,
    session_key as dd_session_key,
    set_dash_state,
)

bp = Blueprint("routes", __name__)

_AI_HIST_CAP = 48  # pairs of user/assistant; trimmed server-side


def _ai_hist_get(lesson_id: int) -> list[dict[str, str]]:
    bucket = session.get("lesson_ai_chats") or {}
    raw = bucket.get(str(lesson_id))
    if not isinstance(raw, list):
        return []
    out: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "")
        content = str(item.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            out.append({"role": role, "content": content})
    return out


def _ai_hist_save(lesson_id: int, hist: list[dict[str, str]]) -> None:
    bucket = dict(session.get("lesson_ai_chats") or {})
    bucket[str(lesson_id)] = hist[-_AI_HIST_CAP:]
    session["lesson_ai_chats"] = bucket
    session.modified = True


def _ai_hist_append(lesson_id: int, role: str, content: str) -> None:
    h = _ai_hist_get(lesson_id)
    h.append({"role": role, "content": content})
    _ai_hist_save(lesson_id, h)


def _ai_hist_clear(lesson_id: int) -> None:
    bucket = dict(session.get("lesson_ai_chats") or {})
    bucket.pop(str(lesson_id), None)
    session["lesson_ai_chats"] = bucket
    session.modified = True


def _effective_grade(user) -> int:
    """Students should always map to a TEKS band for question lookup (DB grade or username fallback)."""
    try:
        gval = user["grade"]
        if gval is not None and int(gval) > 0:
            return int(gval)
    except (TypeError, ValueError):
        pass
    u = (user.get("username") or "").lower()
    if u == "charlie":
        return 6
    if u == "chris":
        return 7
    return 6


def _filter_renderable_mcqs(qs):
    """Templates only render multiple-choice with a JSON list of answers."""
    out = []
    for q in qs:
        it = (q["item_type"] or "multiple_choice").strip().lower()
        if it not in {"multiple_choice", "mcq", ""}:
            continue
        try:
            ch = json.loads(q["choices_json"] or "[]")
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(ch, list) and len(ch) >= 2:
            out.append(q)
    return out


def _letter_for_choice_text(selected_text: str, choices_json: str) -> str:
    try:
        ch_list = json.loads(choices_json or "[]")
    except (json.JSONDecodeError, TypeError):
        return (selected_text or "")[:80]
    if not isinstance(ch_list, list):
        return (selected_text or "")[:80]
    nt = normalize_text(selected_text)
    for i, opt in enumerate(ch_list):
        if normalize_text(str(opt)) == nt:
            return chr(ord("A") + i)
    return (selected_text or "")[:80]


def _pick_random_snake_question(db, subject: str, grade: int):
    qs = _fetch_practice_questions(db, subject, grade)
    if not qs:
        return None
    return random.choice(qs)


def _question_row_to_snake_json(q) -> dict:
    try:
        choices_raw = json.loads(q["choices_json"] or "[]")
    except (json.JSONDecodeError, TypeError):
        return {}
    if not isinstance(choices_raw, list) or len(choices_raw) < 2:
        return {}
    letters = [chr(ord("A") + i) for i in range(len(choices_raw))]
    correct_letter = (q["answer_key"] or "A").strip().upper()
    built = [{"text": str(text), "is_correct": (letters[i] == correct_letter)} for i, text in enumerate(choices_raw)]
    random.shuffle(built)
    return {
        "question_id": str(int(q["id"])),
        "skill": str(q["skill"] or ""),
        "teks": str(q["teks_tag"] or ""),
        "prompt": str(q["prompt"] or ""),
        "choices": built,
    }


def _fetch_practice_questions(db, subject: str, grade: int):
    subject = (subject or "").strip() or "Math"
    lo = max(grade - 1, 1)
    raw = db.execute(
        """
        SELECT * FROM questions
        WHERE subject = ?
          AND (grade IS NULL OR grade IN (?, ?))
        ORDER BY RANDOM()
        LIMIT 12
        """,
        (subject, grade, lo),
    ).fetchall()
    qs = _filter_renderable_mcqs(raw)
    if qs:
        return qs[:5]

    subj_lower = subject.lower()
    alts = []
    if "read" in subj_lower or "elar" in subj_lower or "ela" in subj_lower:
        alts.append("Reading (ELAR)")
    if "math" in subj_lower:
        alts.append("Math")
    for alt in alts:
        if alt == subject:
            continue
        raw = db.execute(
            """
            SELECT * FROM questions
            WHERE subject = ?
              AND (grade IS NULL OR grade IN (?, ?))
            ORDER BY RANDOM()
            LIMIT 12
            """,
            (alt, grade, lo),
        ).fetchall()
        qs = _filter_renderable_mcqs(raw)
        if qs:
            return qs[:5]

    raw = db.execute(
        """
        SELECT * FROM questions
        WHERE (grade IS NULL OR grade BETWEEN ? AND ?)
        ORDER BY RANDOM()
        LIMIT 20
        """,
        (max(grade - 1, 1), min(grade + 2, 12)),
    ).fetchall()
    qs = _filter_renderable_mcqs(raw)
    return qs[:5]


@bp.before_app_request
def _load_user():
    load_logged_in_user()


@bp.get("/")
def index():
    if g.user is None:
        return redirect(url_for("routes.login"))
    return redirect(url_for("routes.today"))


@bp.route("/login", methods=["GET", "POST"])
def login_view():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip().lower()
        password = request.form.get("password") or ""
        user = login(username, password)
        if user is None:
            flash("Login failed. Check username/password.")
        else:
            return redirect(request.args.get("next") or url_for("routes.today"))
    return render_template("login.html")


@bp.post("/logout")
def logout_view():
    logout()
    return redirect(url_for("routes.login"))


@bp.get("/today")
@login_required
def today():
    db = get_db()
    today_s = date.today().isoformat()
    ensure_player_state(g.user["id"])

    # If today's list is empty for this student, let the first plugin generate it.
    existing = db.execute(
        "SELECT COUNT(*) AS c FROM lessons WHERE user_id = ? AND lesson_date = ?",
        (g.user["id"], today_s),
    ).fetchone()["c"]
    if existing == 0:
        try:
            call_first(current_app, "generate_daily_lessons", db, today_s)
        except Exception:
            # Never block the kid's view if a plugin fails.
            pass
        existing = db.execute(
            "SELECT COUNT(*) AS c FROM lessons WHERE user_id = ? AND lesson_date = ?",
            (g.user["id"], today_s),
        ).fetchone()["c"]

    if existing == 0:
        from .db import insert_emergency_lessons

        n = insert_emergency_lessons(db, g.user["id"], today_s, g.user["grade"], g.user["username"])
        if n:
            flash("Backup lessons were added for today so you can play right away.")

    lessons = db.execute(
        """
        SELECT l.*,
               u.display_name,
               u.grade,
               CASE WHEN c.lesson_id IS NULL THEN 0 ELSE 1 END AS is_done
        FROM lessons l
        JOIN users u ON u.id = l.user_id
        LEFT JOIN completions c ON c.lesson_id = l.id
        WHERE l.user_id = ? AND l.lesson_date = ?
        ORDER BY l.sort_order ASC, l.id ASC
        """,
        (g.user["id"], today_s),
    ).fetchall()
    return render_template("today.html", today=today_s, lessons=lessons)


@bp.post("/lesson/<int:lesson_id>/toggle")
@login_required
def toggle_lesson(lesson_id: int):
    db = get_db()
    row = db.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,)).fetchone()
    if row is None or row["user_id"] != g.user["id"]:
        return redirect(url_for("routes.today"))

    done = db.execute("SELECT lesson_id FROM completions WHERE lesson_id = ?", (lesson_id,)).fetchone()
    if done is None:
        db.execute("INSERT INTO completions (lesson_id) VALUES (?)", (lesson_id,))
        add_xp(g.user["id"], 10)
    else:
        db.execute("DELETE FROM completions WHERE lesson_id = ?", (lesson_id,))
    db.commit()
    return redirect(url_for("routes.today"))


def _sqlite_row_as_dict(cur, row) -> dict:
    """Build a plain dict for Jinja — works on all sqlite3.Row / Python combos."""
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, tuple(row)))


def _lesson_uses_fraction_battle(lesson_d: dict) -> bool:
    """
    Math lessons about fractions use the Battle Tetris (skill-gated combat) UI.
    Matches Charlie's /lesson/1 seed ('fractions' in title) and similar rows.
    """
    subj = (lesson_d.get("subject") or "").strip().lower()
    if "math" not in subj:
        return False
    blob = f"{lesson_d.get('title') or ''} {lesson_d.get('notes') or ''}".lower()
    return "fraction" in blob


def _lesson_primary_mode(lesson_d: dict) -> str | None:
    """
    Flagship browser game for this lesson row.

    Prefer ``game:text-detective`` / ``game:discount-dash`` in notes (or title) so
    reordering auto-increment IDs does not change behavior. ID 3 / 4 fallbacks
    remain for older rows seeded without markers.
    """
    blob = f"{lesson_d.get('notes') or ''}\n{lesson_d.get('title') or ''}".lower()
    if "game:text-detective" in blob or "text detective" in blob or "case battle" in blob:
        return "text_detective"
    if "game:discount-dash" in blob or "discount dash" in blob:
        return "discount_dash"
    lid = int(lesson_d["id"])
    if lid == 3:
        return "text_detective"
    if lid == 4:
        return "discount_dash"
    return None


@bp.route("/lesson", methods=["GET"])
@bp.route("/lesson/", methods=["GET"])
@login_required
def lesson_list_redirect():
    """`/lesson` without an id is a common mistake — send students to Today (avoid 404/blank)."""
    return redirect(url_for("routes.today"))


@bp.get("/games")
@login_required
def games_hub():
    """When a deep-linked lesson id fails, kids still land on playable demos + navigation."""
    db = get_db()
    today_s = date.today().isoformat()
    reading_first = db.execute(
        """
        SELECT id, title, subject FROM lessons
        WHERE user_id = ? AND lesson_date = ?
          AND (lower(subject) LIKE '%read%' OR lower(subject) LIKE '%elar%' OR lower(subject) LIKE '%ela%')
        ORDER BY sort_order ASC, id ASC
        LIMIT 1
        """,
        (g.user["id"], today_s),
    ).fetchone()
    return render_template("games_hub.html", reading_first=reading_first, today_s=today_s)


@bp.get("/play")
@login_required
def play_alias():
    """Short URL kids can remember: same as the Games hub."""
    return redirect(url_for("routes.games_hub"))


@bp.get("/lesson/<int:lesson_id>/games")
@login_required
def lesson_games(lesson_id: int):
    db = get_db()
    cur = db.execute(
        "SELECT * FROM lessons WHERE id = ? AND user_id = ?",
        (lesson_id, g.user["id"]),
    )
    lesson = cur.fetchone()
    if lesson is None:
        if db.execute("SELECT id FROM lessons WHERE id = ?", (lesson_id,)).fetchone() is not None:
            flash("That lesson is for another student. Try Games or Today.")
        else:
            flash("No lesson with that ID. Try Games for demos, or Today.")
        return redirect(url_for("routes.games_hub"))
    lesson_d = _sqlite_row_as_dict(cur, lesson)
    return render_template(
        "lesson_games.html",
        lesson=lesson_d,
        primary_mode=_lesson_primary_mode(lesson_d),
        uses_fraction_battle=_lesson_uses_fraction_battle(lesson_d),
    )


def _resolve_story_duel_bundle_id(lesson_id: int | None) -> str | None:
    """Lesson notes ``story_duel_bundle:slug`` wins, then Flask config, then env (see loader)."""
    if lesson_id is not None:
        db = get_db()
        row = db.execute(
            "SELECT notes FROM lessons WHERE id = ? AND user_id = ?",
            (lesson_id, g.user["id"]),
        ).fetchone()
        if row:
            bid = bundle_id_from_lesson_notes(row["notes"] or "")
            if bid:
                return bid
    cfg = current_app.config.get("STORY_DUEL_BUNDLE_ID")
    if cfg:
        return str(cfg).strip()
    env_b = (os.environ.get("STORY_DUEL_BUNDLE_ID") or "").strip()
    return env_b or None


def _story_duel_start_response(lesson_id: int | None) -> dict:
    ensure_player_state(g.user["id"])
    bid = _resolve_story_duel_bundle_id(lesson_id)
    bundle = load_story_bundle(bid)
    state = initial_state(bundle_id=str(bundle["id"]), user_id=int(g.user["id"]))
    secret = str(current_app.config.get("SECRET_KEY") or "")
    duel_token = encode_duel_state(secret, state)
    return {"ok": True, "bundle": serialize_bundle_public(bundle), "duel_token": duel_token}


def _story_duel_round_response(lesson_id: int | None) -> tuple[dict, int]:
    if not request.is_json:
        return {"error": "expected application/json"}, 400
    payload = request.get_json(silent=True) or {}
    answer = str(payload.get("answer") or "").strip()
    try:
        ms_elapsed = int(payload.get("ms_elapsed") or 0)
    except (TypeError, ValueError):
        ms_elapsed = 0

    token = payload.get("duel_token") or payload.get("duelToken")
    if not token or not isinstance(token, str):
        return {"error": "missing duel_token — tap Begin Story Duel again"}, 400

    secret = str(current_app.config.get("SECRET_KEY") or "")
    raw = decode_duel_state(secret, token.strip())
    if raw is None:
        return {"error": "invalid duel token — start the duel again"}, 400
    st = coerce_duel_state(raw)
    if st is None:
        return {"error": "corrupt duel state — start again"}, 400
    if st["uid"] != int(g.user["id"]):
        return {"error": "wrong account for this duel — start again"}, 400
    if st.get("done"):
        return {"error": "duel already finished"}, 400

    bid = st.get("bundle_id") or get_default_bundle_id()
    st["bundle_id"] = bid
    bundle = load_story_bundle(bid)
    result = apply_round(answer=answer, ms_elapsed=max(0, ms_elapsed), bundle=bundle, state=st)
    xp_earned = 0
    if result.get("battle_end"):
        xp_earned = xp_for_outcome(result["battle_end"])
        if xp_earned and not st.get("xp_awarded"):
            add_xp(g.user["id"], xp_earned)
            st["xp_awarded"] = True

    duel_token = encode_duel_state(secret, st)

    out = {
        "ok": True,
        "correct": result["correct"],
        "player_hp": result["player_hp"],
        "ai_hp": result["ai_hp"],
        "streak": result["streak"],
        "round_index": result["round_index"],
        "narrative": result["narrative"],
        "battle_end": result["battle_end"],
        "next_round": result["next_round"],
        "xp_earned": xp_earned,
        "grading_source": result.get("grading_source"),
        "grading_feedback": result.get("grading_feedback"),
        "duel_token": duel_token,
    }
    return out, 200


@bp.get("/lesson/<int:lesson_id>")
@login_required
def lesson_detail(lesson_id: int):
    db = get_db()
    try:
        cur = db.execute(
            """
            SELECT l.*,
                   CASE WHEN c.lesson_id IS NULL THEN 0 ELSE 1 END AS is_done
            FROM lessons l
            LEFT JOIN completions c ON c.lesson_id = l.id
            WHERE l.id = ? AND l.user_id = ?
            """,
            (lesson_id, g.user["id"]),
        )
        lesson = cur.fetchone()
        if lesson is None:
            other = db.execute("SELECT id FROM lessons WHERE id = ?", (lesson_id,)).fetchone()
            if other is not None:
                flash("That lesson belongs to another login. Open Games for demos, or use Today for your list.")
            else:
                flash(
                    "No lesson with that ID on your account (links like /lesson/2 depend on your database). "
                    "Try Games for Story Duel demo, or open Today."
                )
            return redirect(url_for("routes.games_hub"))
        lesson_d = _sqlite_row_as_dict(cur, lesson)
        ai_ctx = {
            "lesson": lesson_d,
            "ai_history": _ai_hist_get(lesson_id),
            "ai_chat_url": url_for("routes.lesson_ai_chat", lesson_id=lesson_id),
        }
        mode = _lesson_primary_mode(lesson_d)
        if mode == "text_detective":
            ai_ctx.update(
                is_demo=False,
                url_start=url_for("routes.api_text_detective_start", lesson_id=lesson_id),
                url_step=url_for("routes.api_text_detective_step", lesson_id=lesson_id),
                url_reflect=url_for("routes.api_text_detective_reflect", lesson_id=lesson_id),
            )
            return render_template("lesson_text_detective.html", **ai_ctx)
        if mode == "discount_dash":
            ai_ctx.update(
                is_demo=False,
                intro=dd_public_intro(),
                url_start=url_for("routes.api_discount_dash_start", lesson_id=lesson_id),
                url_answer=url_for("routes.api_discount_dash_answer", lesson_id=lesson_id),
                url_method=url_for("routes.api_discount_dash_method", lesson_id=lesson_id),
                url_finish=url_for("routes.api_discount_dash_finish", lesson_id=lesson_id),
            )
            return render_template("lesson_discount_dash.html", **ai_ctx)
        if _lesson_uses_fraction_battle(lesson_d):
            return render_template("lesson_fraction_battle.html", **ai_ctx)
        return render_template("lesson.html", **ai_ctx)
    except Exception:
        current_app.logger.exception("lesson_detail failed")
        flash("Something went wrong opening that lesson. Try Games or Today.")
        return redirect(url_for("routes.games_hub"))


@bp.post("/lesson/<int:lesson_id>/ai-chat")
@login_required
def lesson_ai_chat(lesson_id: int):
    """
    JSON API for the on-page AI lesson coach (Ollama /api/chat).
    Conversation is stored in the Flask session per lesson_id.
    """
    if not request.is_json:
        return jsonify(error="send Content-Type: application/json"), 400
    payload = request.get_json(silent=True) or {}
    if payload.get("reset"):
        _ai_hist_clear(lesson_id)
        return jsonify(ok=True, cleared=True)

    db = get_db()
    cur = db.execute(
        "SELECT * FROM lessons WHERE id = ? AND user_id = ?",
        (lesson_id, g.user["id"]),
    )
    lesson = cur.fetchone()
    if lesson is None:
        return jsonify(error="lesson not found"), 404

    msg = (payload.get("message") or "").strip()
    if not msg or len(msg) > 8000:
        return jsonify(error="message too long or empty"), 400

    lesson_d = _sqlite_row_as_dict(cur, lesson)
    display_name = str(g.user["display_name"] or g.user["username"] or "student")
    sys_prompt = build_lesson_system_prompt(
        title=str(lesson_d.get("title") or ""),
        subject=str(lesson_d.get("subject") or ""),
        grade=g.user["grade"],
        display_name=display_name,
        notes=str(lesson_d.get("notes") or ""),
    )
    hist = _ai_hist_get(lesson_id)
    messages: list[dict[str, str]] = [{"role": "system", "content": sys_prompt}]
    for m in hist:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": msg})

    reply, ok = ollama_chat(messages)
    if ok:
        _ai_hist_append(lesson_id, "user", msg)
        _ai_hist_append(lesson_id, "assistant", reply)
    return jsonify(reply=reply, offline=not ok)


@bp.route("/practice/<int:lesson_id>", methods=["GET", "POST"])
@login_required
def practice(lesson_id: int):
    """
    Practice Game V1:
    - derives subject/grade from the lesson
    - renders MCQ items from the question bank
    - grades via grading helpers
    - persists attempts
    """
    db = get_db()
    ensure_player_state(g.user["id"])

    cur = db.execute("SELECT * FROM lessons WHERE id = ? AND user_id = ?", (lesson_id, g.user["id"]))
    lesson = cur.fetchone()
    if lesson is None:
        if db.execute("SELECT id FROM lessons WHERE id = ?", (lesson_id,)).fetchone() is not None:
            flash("That practice is for another student’s lesson. Open Today for your list.")
        return redirect(url_for("routes.today"))

    if request.method == "GET" and (request.args.get("mode") or "").strip().lower() == "snake":
        return redirect(url_for("routes.snake_practice", lesson_id=lesson_id))

    subject = (lesson["subject"] or "").strip() or "Math"
    grade = _effective_grade(g.user)
    qs = _fetch_practice_questions(db, subject, grade)
    lesson_d = _sqlite_row_as_dict(cur, lesson)

    if request.method == "POST":
        if not qs:
            flash("No practice questions for that lesson yet. Pick Math or Reading, or ask a parent.")
            return redirect(url_for("routes.practice", lesson_id=lesson_id))
        total = 0
        correct = 0
        per_q = []
        for q in qs:
            qid = q["id"]
            total += 1
            selected = (request.form.get(f"q_{qid}") or "").strip()
            is_correct = 1 if grade_mcq(selected, q["answer_key"]) else 0
            correct += is_correct
            per_q.append((qid, selected, is_correct))

        session_id = f"lesson-{lesson_id}-{date.today().isoformat()}-{uuid4().hex}"
        for qid, selected, is_correct in per_q:
            db.execute(
                "INSERT INTO question_attempts (user_id, question_id, selected_key, is_correct, session_id) VALUES (?,?,?,?,?)",
                (g.user["id"], qid, selected or None, int(is_correct), session_id),
            )
        db.commit()

        add_xp(g.user["id"], correct * 10)

        return redirect(
            url_for(
                "routes.practice_result",
                lesson_id=lesson_id,
                subject=subject,
                correct=correct,
                total=total,
            )
        )

    return render_template("practice.html", lesson=lesson_d, subject=subject, questions=qs)


@bp.get("/practice/<int:lesson_id>/result")
@login_required
def practice_result(lesson_id: int):
    subject = request.args.get("subject") or ""
    correct = int(request.args.get("correct") or 0)
    total = int(request.args.get("total") or 0)
    return render_template("practice_result.html", lesson_id=lesson_id, subject=subject, correct=correct, total=total)


@bp.get("/lesson/<int:lesson_id>/snake")
@login_required
def snake_practice(lesson_id: int):
    db = get_db()
    cur = db.execute(
        "SELECT * FROM lessons WHERE id = ? AND user_id = ?",
        (lesson_id, g.user["id"]),
    )
    lesson = cur.fetchone()
    if lesson is None:
        if db.execute("SELECT id FROM lessons WHERE id = ?", (lesson_id,)).fetchone() is not None:
            flash("That Snake practice is for another student’s lesson. Open Today for your list.")
        return redirect(url_for("routes.today"))
    lesson_d = _sqlite_row_as_dict(cur, lesson)
    opponent = snake_opponent_for_lesson(str(lesson_d.get("subject") or ""))
    return render_template("snake_practice.html", lesson=lesson_d, opponent=opponent)


@bp.get("/api/lesson/<int:lesson_id>/snake-question")
@login_required
def api_snake_question(lesson_id: int):
    db = get_db()
    lesson = db.execute(
        "SELECT * FROM lessons WHERE id = ? AND user_id = ?",
        (lesson_id, g.user["id"]),
    ).fetchone()
    if lesson is None:
        return jsonify(error="lesson not found"), 404

    q_subject = snake_question_subject_for_lesson(str(lesson["subject"] or ""))
    grade = _effective_grade(g.user)
    row = _pick_random_snake_question(db, q_subject, grade)
    if row is None:
        return jsonify(error="no questions"), 404
    payload = _question_row_to_snake_json(row)
    if not payload:
        return jsonify(error="no questions"), 404
    return jsonify(payload)


@bp.post("/api/lesson/<int:lesson_id>/snake-answer")
@login_required
def api_snake_answer(lesson_id: int):
    if not request.is_json:
        return jsonify(error="expected application/json"), 400
    db = get_db()
    ensure_player_state(g.user["id"])

    lesson = db.execute(
        "SELECT * FROM lessons WHERE id = ? AND user_id = ?",
        (lesson_id, g.user["id"]),
    ).fetchone()
    if lesson is None:
        return jsonify(error="lesson not found"), 404

    payload = request.get_json(silent=True) or {}
    qid_raw = payload.get("question_id")
    try:
        qid = int(qid_raw)
    except (TypeError, ValueError):
        return jsonify(error="bad question_id"), 400

    selected_text = str(payload.get("selected_text") or "").strip()
    qrow = db.execute("SELECT * FROM questions WHERE id = ?", (qid,)).fetchone()
    if qrow is None:
        return jsonify(error="unknown question"), 400

    actually_correct = bool(grade_mcq_choice_text(selected_text, qrow["choices_json"], qrow["answer_key"]))
    session_id = f"snake-{lesson_id}-{date.today().isoformat()}-{uuid4().hex}"
    selected_key = _letter_for_choice_text(selected_text, qrow["choices_json"])
    db.execute(
        "INSERT INTO question_attempts (user_id, question_id, selected_key, is_correct, session_id) VALUES (?,?,?,?,?)",
        (g.user["id"], qid, selected_key or None, int(actually_correct), session_id),
    )
    db.commit()

    xp_earned = 10 if actually_correct else 0
    if xp_earned:
        add_xp(g.user["id"], xp_earned)

    return jsonify(
        ok=True,
        lesson_id=lesson_id,
        question_id=str(qid),
        correct=actually_correct,
        xp_earned=xp_earned,
        teks=str(payload.get("teks") or qrow["teks_tag"] or ""),
        skill=str(payload.get("skill") or qrow["skill"] or ""),
    )


@bp.get("/lesson/<int:lesson_id>/story-duel")
@login_required
def story_duel_play(lesson_id: int):
    db = get_db()
    cur = db.execute(
        "SELECT * FROM lessons WHERE id = ? AND user_id = ?",
        (lesson_id, g.user["id"]),
    )
    lesson = cur.fetchone()
    if lesson is None:
        if db.execute("SELECT id FROM lessons WHERE id = ?", (lesson_id,)).fetchone() is not None:
            flash("That Story Duel is tied to another student’s lesson. Try the demo on Games.")
        return redirect(url_for("routes.games_hub"))
    lesson_d = _sqlite_row_as_dict(cur, lesson)
    ensure_player_state(g.user["id"])
    return render_template(
        "story_duel.html",
        lesson=lesson_d,
        is_demo=False,
        url_start=url_for("routes.api_story_duel_start", lesson_id=lesson_id),
        url_round=url_for("routes.api_story_duel_round", lesson_id=lesson_id),
        url_exit=url_for("routes.lesson_games", lesson_id=lesson_id),
    )


@bp.get("/demo/story-duel")
@login_required
def story_duel_demo():
    ensure_player_state(g.user["id"])
    return render_template(
        "story_duel.html",
        lesson=None,
        is_demo=True,
        url_start=url_for("routes.api_story_duel_demo_start"),
        url_round=url_for("routes.api_story_duel_demo_round"),
        url_exit=url_for("routes.games_hub"),
    )


@bp.post("/api/lesson/<int:lesson_id>/story-duel/start")
@login_required
def api_story_duel_start(lesson_id: int):
    db = get_db()
    if db.execute("SELECT id FROM lessons WHERE id = ? AND user_id = ?", (lesson_id, g.user["id"])).fetchone() is None:
        return jsonify(error="lesson not found"), 404
    ensure_player_state(g.user["id"])
    return jsonify(_story_duel_start_response(lesson_id))


@bp.post("/api/lesson/<int:lesson_id>/story-duel/round")
@login_required
def api_story_duel_round(lesson_id: int):
    db = get_db()
    if db.execute("SELECT id FROM lessons WHERE id = ? AND user_id = ?", (lesson_id, g.user["id"])).fetchone() is None:
        return jsonify(error="lesson not found"), 404
    ensure_player_state(g.user["id"])
    payload, status = _story_duel_round_response(lesson_id)
    if status != 200:
        return jsonify(payload), status
    return jsonify(payload)


@bp.post("/api/story-duel/demo/start")
@login_required
def api_story_duel_demo_start():
    ensure_player_state(g.user["id"])
    return jsonify(_story_duel_start_response(None))


@bp.post("/api/story-duel/demo/round")
@login_required
def api_story_duel_demo_round():
    ensure_player_state(g.user["id"])
    payload, status = _story_duel_round_response(None)
    if status != 200:
        return jsonify(payload), status
    return jsonify(payload)


def _verify_lesson_owner(lesson_id: int) -> bool:
    db = get_db()
    return (
        db.execute("SELECT id FROM lessons WHERE id = ? AND user_id = ?", (lesson_id, g.user["id"])).fetchone()
        is not None
    )


@bp.post("/api/lesson/<int:lesson_id>/fraction-battle/xp")
@login_required
def api_fraction_battle_xp(lesson_id: int):
    if not _verify_lesson_owner(lesson_id):
        return jsonify(error="lesson not found"), 404
    if not request.is_json:
        return jsonify(error="json required"), 400
    ensure_player_state(g.user["id"])
    gate = f"fb_xp_{lesson_id}_{g.user['id']}"
    if session.get(gate):
        return jsonify(ok=True, xp=0, duplicate=True)
    payload = request.get_json(silent=True) or {}
    won = bool(payload.get("won"))
    xp = 28 if won else 10
    add_xp(g.user["id"], xp)
    session[gate] = True
    session.modified = True
    return jsonify(ok=True, xp=xp)


# --- Text Detective (Case Battle) + Discount Dash ---------------------------------


@bp.get("/demo/text-detective")
@login_required
def text_detective_demo():
    ensure_player_state(g.user["id"])
    return render_template(
        "lesson_text_detective.html",
        lesson=None,
        is_demo=True,
        url_start=url_for("routes.api_text_detective_demo_start"),
        url_step=url_for("routes.api_text_detective_demo_step"),
        url_reflect=url_for("routes.api_text_detective_demo_reflect"),
    )


@bp.get("/demo/discount-dash")
@login_required
def discount_dash_demo():
    ensure_player_state(g.user["id"])
    return render_template(
        "lesson_discount_dash.html",
        lesson=None,
        is_demo=True,
        intro=dd_public_intro(),
        url_start=url_for("routes.api_discount_dash_demo_start"),
        url_answer=url_for("routes.api_discount_dash_demo_answer"),
        url_method=url_for("routes.api_discount_dash_demo_method"),
        url_finish=url_for("routes.api_discount_dash_demo_finish"),
    )


@bp.post("/api/lesson/<int:lesson_id>/text-detective/start")
@login_required
def api_text_detective_start(lesson_id: int):
    if not _verify_lesson_owner(lesson_id):
        return jsonify(error="lesson not found"), 404
    ensure_player_state(g.user["id"])
    k = td_session_key(lesson_id, g.user["id"])
    detective_set_state(session, k, td_initial_state())
    return jsonify(ok=True, bundle=detective_client_bundle())


@bp.post("/api/lesson/<int:lesson_id>/text-detective/step")
@login_required
def api_text_detective_step(lesson_id: int):
    if not _verify_lesson_owner(lesson_id):
        return jsonify(error="lesson not found"), 404
    ensure_player_state(g.user["id"])
    if not request.is_json:
        return jsonify(error="json required"), 400
    k = td_session_key(lesson_id, g.user["id"])
    st = detective_get_state(session, k)
    if st is None:
        return jsonify(error="start first"), 400
    payload, code = td_process_step(state=st, payload=request.get_json(silent=True) or {}, bundle=td_public_bundle())
    detective_set_state(session, k, st)
    return jsonify(payload), code


@bp.post("/api/lesson/<int:lesson_id>/text-detective/reflect")
@login_required
def api_text_detective_reflect(lesson_id: int):
    if not _verify_lesson_owner(lesson_id):
        return jsonify(error="lesson not found"), 404
    ensure_player_state(g.user["id"])
    if not request.is_json:
        return jsonify(error="json required"), 400
    k = td_session_key(lesson_id, g.user["id"])
    st = detective_get_state(session, k)
    if st is None:
        return jsonify(error="no session"), 400
    if st.get("paid_xp"):
        return jsonify(ok=True, paid=True)
    note = str((request.get_json(silent=True) or {}).get("note") or "")
    _out, _c = td_process_reflection(state=st, text=note)
    total = int(st.get("xp_total") or 0)
    if total > 0:
        add_xp(g.user["id"], total)
    st["paid_xp"] = True
    detective_set_state(session, k, st)
    session.pop(k, None)
    return jsonify(ok=True, xp_awarded=total)


@bp.post("/api/text-detective/demo/start")
@login_required
def api_text_detective_demo_start():
    ensure_player_state(g.user["id"])
    k = td_session_key(None, g.user["id"])
    detective_set_state(session, k, td_initial_state())
    return jsonify(ok=True, bundle=detective_client_bundle())


@bp.post("/api/text-detective/demo/step")
@login_required
def api_text_detective_demo_step():
    ensure_player_state(g.user["id"])
    if not request.is_json:
        return jsonify(error="json required"), 400
    k = td_session_key(None, g.user["id"])
    st = detective_get_state(session, k)
    if st is None:
        return jsonify(error="start first"), 400
    payload, code = td_process_step(state=st, payload=request.get_json(silent=True) or {}, bundle=td_public_bundle())
    detective_set_state(session, k, st)
    return jsonify(payload), code


@bp.post("/api/text-detective/demo/reflect")
@login_required
def api_text_detective_demo_reflect():
    ensure_player_state(g.user["id"])
    if not request.is_json:
        return jsonify(error="json required"), 400
    k = td_session_key(None, g.user["id"])
    st = detective_get_state(session, k)
    if st is None:
        return jsonify(error="no session"), 400
    if st.get("paid_xp"):
        return jsonify(ok=True, paid=True)
    note = str((request.get_json(silent=True) or {}).get("note") or "")
    td_process_reflection(state=st, text=note)
    total = int(st.get("xp_total") or 0)
    if total > 0:
        add_xp(g.user["id"], total)
    st["paid_xp"] = True
    detective_set_state(session, k, st)
    session.pop(k, None)
    return jsonify(ok=True, xp_awarded=total)


@bp.post("/api/lesson/<int:lesson_id>/discount-dash/start")
@login_required
def api_discount_dash_start(lesson_id: int):
    if not _verify_lesson_owner(lesson_id):
        return jsonify(error="lesson not found"), 404
    ensure_player_state(g.user["id"])
    k = dd_session_key(lesson_id, g.user["id"])
    set_dash_state(session, k, dd_initial_state())
    st = get_dash_state(session, k) or {}
    return jsonify(ok=True, intro=dd_public_intro(), item=st.get("current"))


@bp.post("/api/lesson/<int:lesson_id>/discount-dash/answer")
@login_required
def api_discount_dash_answer(lesson_id: int):
    if not _verify_lesson_owner(lesson_id):
        return jsonify(error="lesson not found"), 404
    ensure_player_state(g.user["id"])
    if not request.is_json:
        return jsonify(error="json required"), 400
    k = dd_session_key(lesson_id, g.user["id"])
    st = get_dash_state(session, k)
    if st is None:
        return jsonify(error="start first"), 400
    body = request.get_json(silent=True) or {}
    payload, code = dd_process_answer(state=st, raw_answer=body.get("answer"), ms=int(body.get("ms_elapsed") or 0))
    set_dash_state(session, k, st)
    return jsonify(payload), code


@bp.post("/api/lesson/<int:lesson_id>/discount-dash/method")
@login_required
def api_discount_dash_method(lesson_id: int):
    if not _verify_lesson_owner(lesson_id):
        return jsonify(error="lesson not found"), 404
    ensure_player_state(g.user["id"])
    k = dd_session_key(lesson_id, g.user["id"])
    st = get_dash_state(session, k)
    if st is None:
        return jsonify(error="no session"), 400
    m = str((request.get_json(silent=True) or {}).get("method") or "")
    payload, code = dd_process_method_bonus(state=st, method=m)
    set_dash_state(session, k, st)
    return jsonify(payload), code


@bp.post("/api/lesson/<int:lesson_id>/discount-dash/finish")
@login_required
def api_discount_dash_finish(lesson_id: int):
    if not _verify_lesson_owner(lesson_id):
        return jsonify(error="lesson not found"), 404
    ensure_player_state(g.user["id"])
    k = dd_session_key(lesson_id, g.user["id"])
    st = get_dash_state(session, k)
    if st is None:
        return jsonify(error="no session"), 400
    if st.get("paid_xp"):
        return jsonify(ok=True, duplicate=True)
    total = int(st.get("xp_bank") or 0)
    if total > 0:
        add_xp(g.user["id"], total)
    st["paid_xp"] = True
    set_dash_state(session, k, st)
    session.pop(k, None)
    return jsonify(ok=True, xp_awarded=total)


@bp.post("/api/discount-dash/demo/start")
@login_required
def api_discount_dash_demo_start():
    ensure_player_state(g.user["id"])
    k = dd_session_key(None, g.user["id"])
    set_dash_state(session, k, dd_initial_state())
    st = get_dash_state(session, k) or {}
    return jsonify(ok=True, intro=dd_public_intro(), item=st.get("current"))


@bp.post("/api/discount-dash/demo/answer")
@login_required
def api_discount_dash_demo_answer():
    ensure_player_state(g.user["id"])
    if not request.is_json:
        return jsonify(error="json required"), 400
    k = dd_session_key(None, g.user["id"])
    st = get_dash_state(session, k)
    if st is None:
        return jsonify(error="start first"), 400
    body = request.get_json(silent=True) or {}
    payload, code = dd_process_answer(state=st, raw_answer=body.get("answer"), ms=int(body.get("ms_elapsed") or 0))
    set_dash_state(session, k, st)
    return jsonify(payload), code


@bp.post("/api/discount-dash/demo/method")
@login_required
def api_discount_dash_demo_method():
    ensure_player_state(g.user["id"])
    k = dd_session_key(None, g.user["id"])
    st = get_dash_state(session, k)
    if st is None:
        return jsonify(error="no session"), 400
    m = str((request.get_json(silent=True) or {}).get("method") or "")
    payload, code = dd_process_method_bonus(state=st, method=m)
    set_dash_state(session, k, st)
    return jsonify(payload), code


@bp.post("/api/discount-dash/demo/finish")
@login_required
def api_discount_dash_demo_finish():
    ensure_player_state(g.user["id"])
    k = dd_session_key(None, g.user["id"])
    st = get_dash_state(session, k)
    if st is None:
        return jsonify(error="no session"), 400
    if st.get("paid_xp"):
        return jsonify(ok=True, duplicate=True)
    total = int(st.get("xp_bank") or 0)
    if total > 0:
        add_xp(g.user["id"], total)
    st["paid_xp"] = True
    set_dash_state(session, k, st)
    session.pop(k, None)
    return jsonify(ok=True, xp_awarded=total)


@bp.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    db = get_db()
    if request.method == "POST":
        message = (request.form.get("message") or "").strip()
        rating_raw = (request.form.get("rating") or "").strip()
        rating = None
        if rating_raw.isdigit():
            rating = int(rating_raw)
            if rating < 1 or rating > 5:
                rating = None

        if not message:
            flash("Please type a message.")
        else:
            db.execute(
                "INSERT INTO feedback (user_id, rating, message, context_json) VALUES (?,?,?,?)",
                (g.user["id"], rating, message, "{}"),
            )
            db.commit()
            flash("Thanks! Feedback sent.")
            return redirect(url_for("routes.feedback"))

    return render_template("feedback.html")


@bp.get("/adventure")
@login_required
def adventure():
    db = get_db()
    ensure_player_state(g.user["id"])
    state = db.execute("SELECT * FROM player_state WHERE user_id = ?", (g.user["id"],)).fetchone()
    next_boss_level = get_next_boss_level(int(state["level"]))
    next_boss_subject = pick_boss_subject(g.user)
    gate_ok, gate_reason = can_level_up(build_student_gate_snapshot(g.user["id"]))
    return render_template(
        "adventure.html",
        state=state,
        next_boss_level=next_boss_level,
        next_boss_subject=next_boss_subject,
        gate_ok=gate_ok,
        gate_reason=gate_reason,
    )


@bp.get("/admin")
@admin_required
def admin_home():
    db = get_db()
    users = db.execute("SELECT id, username, display_name, grade, is_admin FROM users ORDER BY is_admin DESC, grade ASC, display_name ASC").fetchall()
    return render_template("admin_home.html", users=users)


@bp.route("/admin/users/<int:user_id>", methods=["GET", "POST"])
@admin_required
def admin_user(user_id: int):
    db = get_db()
    user = db.execute("SELECT id, username, display_name, grade, is_admin FROM users WHERE id = ?", (user_id,)).fetchone()
    if user is None:
        return redirect(url_for("routes.admin_home"))

    if request.method == "POST":
        new_pw = request.form.get("new_password") or ""
        if len(new_pw) < 6:
            flash("Password must be at least 6 characters.")
        else:
            db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (generate_password_hash(new_pw), user_id))
            db.commit()
            flash("Password updated.")
            return redirect(url_for("routes.admin_user", user_id=user_id))

    return render_template("admin_user.html", user=user)


@bp.route("/admin/lessons", methods=["GET", "POST"])
@admin_required
def admin_lessons():
    db = get_db()
    selected_date = (request.values.get("date") or date.today().isoformat()).strip()
    selected_user = request.values.get("user_id")

    users = db.execute("SELECT id, display_name, grade FROM users WHERE is_admin = 0 ORDER BY grade ASC, display_name ASC").fetchall()
    if selected_user is None and len(users) > 0:
        selected_user = str(users[0]["id"])

    if request.method == "POST" and request.form.get("action") == "add":
        if selected_user is None:
            flash("Create a student user first.")
        else:
            subject = (request.form.get("subject") or "").strip()
            title = (request.form.get("title") or "").strip()
            notes = (request.form.get("notes") or "").strip()
            sort_order = int(request.form.get("sort_order") or 0)
            if not subject or not title:
                flash("Subject and Title are required.")
            else:
                db.execute(
                    "INSERT INTO lessons (user_id, lesson_date, subject, title, notes, sort_order) VALUES (?,?,?,?,?,?)",
                    (int(selected_user), selected_date, subject, title, notes, sort_order),
                )
                db.commit()
                flash("Lesson added.")
                return redirect(url_for("routes.admin_lessons", date=selected_date, user_id=selected_user))

    lessons = []
    if selected_user is not None:
        lessons = db.execute(
            """
            SELECT l.*,
                   CASE WHEN c.lesson_id IS NULL THEN 0 ELSE 1 END AS is_done
            FROM lessons l
            LEFT JOIN completions c ON c.lesson_id = l.id
            WHERE l.user_id = ? AND l.lesson_date = ?
            ORDER BY l.sort_order ASC, l.id ASC
            """,
            (int(selected_user), selected_date),
        ).fetchall()

    return render_template(
        "admin_lessons.html",
        users=users,
        selected_user=selected_user,
        selected_date=selected_date,
        lessons=lessons,
    )


@bp.post("/admin/lessons/<int:lesson_id>/delete")
@admin_required
def admin_delete_lesson(lesson_id: int):
    db = get_db()
    db.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
    db.commit()
    flash("Lesson deleted.")
    return redirect(url_for("routes.admin_lessons", date=request.args.get("date"), user_id=request.args.get("user_id")))


@bp.route("/admin/lessons/<int:lesson_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_lesson(lesson_id: int):
    db = get_db()
    lesson = db.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,)).fetchone()
    if lesson is None:
        return redirect(url_for("routes.admin_lessons"))

    if request.method == "POST":
        subject = (request.form.get("subject") or "").strip()
        title = (request.form.get("title") or "").strip()
        notes = (request.form.get("notes") or "").strip()
        sort_order = int(request.form.get("sort_order") or 0)
        if not subject or not title:
            flash("Subject and Title are required.")
        else:
            db.execute(
                "UPDATE lessons SET subject=?, title=?, notes=?, sort_order=? WHERE id=?",
                (subject, title, notes, sort_order, lesson_id),
            )
            db.commit()
            flash("Lesson updated.")
            # Return to lesson list context if provided
            return redirect(
                url_for(
                    "routes.admin_lessons",
                    date=request.args.get("date") or lesson["lesson_date"],
                    user_id=request.args.get("user_id") or lesson["user_id"],
                )
            )

    return render_template("admin_edit_lesson.html", lesson=lesson)


@bp.get("/admin/feedback")
@admin_required
def admin_feedback():
    db = get_db()
    items = db.execute(
        """
        SELECT f.id, f.created_at, f.rating, f.message, u.username, u.display_name
        FROM feedback f
        LEFT JOIN users u ON u.id = f.user_id
        ORDER BY f.id DESC
        LIMIT 200
        """
    ).fetchall()
    return render_template("admin_feedback.html", items=items)


@bp.route("/boss/<int:boss_level>", methods=["GET", "POST"])
@login_required
def boss_fight(boss_level: int):
    """
    Boss Fight V1:
    - chooses a subject (Chris -> Reading dragon)
    - pulls a small mixed set of TEKS-tagged multiple choice questions
    - grades, records attempts + assessment, awards XP on correct answers
    """
    db = get_db()
    ensure_player_state(g.user["id"])

    subject = pick_boss_subject(g.user)
    grade = _effective_grade(g.user)

    # Select a small question set (later: adapt to weaknesses + tier difficulty distribution)
    raw = db.execute(
        """
        SELECT * FROM questions
        WHERE subject = ?
          AND (grade IS NULL OR grade IN (?, ?))
        ORDER BY RANDOM()
        LIMIT 16
        """,
        (subject, grade, max(grade - 1, 1)),
    ).fetchall()
    qs = _filter_renderable_mcqs(raw)[:6]
    if len(qs) < 4:
        raw = db.execute(
            """
            SELECT * FROM questions
            WHERE (grade IS NULL OR grade BETWEEN ? AND ?)
            ORDER BY RANDOM()
            LIMIT 24
            """,
            (max(grade - 1, 1), min(grade + 2, 12)),
        ).fetchall()
        qs = _filter_renderable_mcqs(raw)[:6]

    if request.method == "POST":
        # Grade
        total = 0
        correct = 0
        per_q = []
        for q in qs:
            qid = q["id"]
            total += 1
            item_type = (q["item_type"] or "multiple_choice").strip().lower()
            if item_type in {"multiple_choice", "mcq"}:
                selected = (request.form.get(f"q_{qid}") or "").strip()
                is_correct = 1 if grade_mcq(selected, q["answer_key"]) else 0
            elif item_type in {"multi_select", "multiple_select"}:
                selected_list = [s.strip() for s in request.form.getlist(f"q_{qid}") if (s or "").strip()]
                correct_list = [s.strip() for s in (q["answer_key"] or "").split(",") if s.strip()]
                is_correct = 1 if grade_multi_select(selected_list, correct_list) else 0
                selected = ",".join(selected_list)
            elif item_type in {"ordering", "order"}:
                # Expect a comma-separated sequence (UI can provide richer ordering later).
                selected_order = [s.strip() for s in (request.form.get(f"q_{qid}") or "").split(",") if s.strip()]
                correct_order = [s.strip() for s in (q["answer_key"] or "").split(",") if s.strip()]
                is_correct = 1 if grade_ordering(selected_order, correct_order) else 0
                selected = ",".join(selected_order)
            elif item_type in {"short_response", "short", "free_response"}:
                selected = (request.form.get(f"q_{qid}") or "").strip()
                is_correct = 1 if grade_short_response(selected, q["answer_key"]) else 0
            else:
                selected = (request.form.get(f"q_{qid}") or "").strip()
                is_correct = 1 if grade_mcq(selected, q["answer_key"]) else 0
            correct += is_correct
            per_q.append((qid, selected, is_correct, q["answer_key"], q["teks_tag"], q["skill"]))

        score = float(correct)
        max_score = float(total)
        passed = 1 if (max_score > 0 and (score / max_score) >= 0.8) else 0

        # record assessment summary (subject-level for v1)
        db.execute(
            "INSERT INTO assessments (user_id, assessed_on, subject, score, max_score, notes) VALUES (?,?,?,?,?,?)",
            (g.user["id"], date.today().isoformat(), subject, score, max_score, f"Boss L{boss_level}"),
        )

        # record attempts (session_id simplified for v1)
        session_id = f"{g.user['id']}-{boss_level}-{date.today().isoformat()}-{uuid4().hex}"
        for qid, selected, is_correct, _ans, _teks, _skill in per_q:
            db.execute(
                "INSERT INTO question_attempts (user_id, question_id, selected_key, is_correct, session_id) VALUES (?,?,?,?,?)",
                (g.user["id"], qid, selected or None, int(is_correct), session_id),
            )

        db.execute(
            """
            INSERT INTO boss_attempts (user_id, boss_level, subject, finished_at, score, max_score, passed, session_id, details_json)
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (g.user["id"], boss_level, subject, None, score, max_score, passed, session_id, "{}"),
        )

        db.commit()

        # XP model v1 (correct answer = 10; pass bonus = 50)
        add_xp(g.user["id"], correct * 10 + (50 if passed else 0))

        drop = None
        if max_score > 0:
            # Boss fights always have a drop, with rarity influenced by score.
            drop = roll_gear(score / max_score, boss=True)
            if drop is not None:
                # Persist the drop into gear tables (idempotent enough for V1).
                gear_key = f"drop_{drop.get('rarity','common')}_{(drop.get('slot') or 'gear').lower()}_{(drop.get('name') or 'item').lower().replace(' ', '_')}"
                existing = db.execute("SELECT id FROM gear WHERE gear_key = ?", (gear_key,)).fetchone()
                if existing is None:
                    db.execute(
                        "INSERT INTO gear (gear_key, slot, name, description, rarity, icon, criteria_json) VALUES (?,?,?,?,?,?,?)",
                        (
                            gear_key,
                            drop.get("slot") or "gear",
                            drop.get("name") or "Mystery Gear",
                            f"Earned from Boss L{boss_level}.",
                            drop.get("rarity") or "common",
                            "🧰",
                            "{}",
                        ),
                    )
                    db.commit()
                    existing = db.execute("SELECT id FROM gear WHERE gear_key = ?", (gear_key,)).fetchone()
                if existing is not None:
                    db.execute(
                        "INSERT OR IGNORE INTO gear_unlocks (user_id, gear_id, reason) VALUES (?,?,?)",
                        (g.user["id"], existing["id"], f"Boss L{boss_level} reward"),
                    )
                    db.commit()

        if passed:
            flash(f"Boss cleared! Score {correct}/{total}.")
        else:
            flash(f"Not yet. Score {correct}/{total}. Train and try again.")

        return redirect(
            url_for(
                "routes.boss_result",
                boss_level=boss_level,
                subject=subject,
                correct=correct,
                total=total,
                passed=passed,
                drop_name=(drop or {}).get("name") or "",
                drop_rarity=(drop or {}).get("rarity") or "",
                drop_slot=(drop or {}).get("slot") or "",
            )
        )

    return render_template("boss.html", boss_level=boss_level, subject=subject, questions=qs)


@bp.get("/boss/<int:boss_level>/result")
@login_required
def boss_result(boss_level: int):
    subject = request.args.get("subject") or ""
    correct = int(request.args.get("correct") or 0)
    total = int(request.args.get("total") or 0)
    passed = int(request.args.get("passed") or 0) == 1
    drop = {
        "name": (request.args.get("drop_name") or "").strip(),
        "rarity": (request.args.get("drop_rarity") or "").strip(),
        "slot": (request.args.get("drop_slot") or "").strip(),
    }
    if not drop["name"]:
        drop = None
    return render_template("boss_result.html", boss_level=boss_level, subject=subject, correct=correct, total=total, passed=passed, drop=drop)


# Alias endpoints for templates
bp.add_url_rule("/login", endpoint="login", view_func=login_view, methods=["GET", "POST"])
bp.add_url_rule("/logout", endpoint="logout", view_func=logout_view, methods=["POST"])

