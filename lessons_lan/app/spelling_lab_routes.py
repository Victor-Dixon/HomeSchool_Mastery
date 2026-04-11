"""
Spelling Lab — browser version for phones/tablets on the LAN (same Wi‑Fi as the PC).
"""

from __future__ import annotations

import random
import time
from typing import Any

from flask import Blueprint, jsonify, render_template, request, session

from spelling_lab_core import (
    FLASH_SHOW_SEC,
    SPRINT_MIN_SEC,
    SPRINT_START_SEC,
    SPRINT_STEP_SEC,
    load_word_list,
    make_skeleton,
    scramble_letters,
    shuffled_pool,
)

from .auth import login_required

bp = Blueprint("spelling_lab", __name__)

SESSION_KEY = "spelling_lab_web_v1"

# Generous typing window after flash (server-side safety net).
_ANSWER_SLACK_SEC = 120.0


def _state() -> dict[str, Any] | None:
    raw = session.get(SESSION_KEY)
    return raw if isinstance(raw, dict) else None


def _save_state(st: dict[str, Any]) -> None:
    session[SESSION_KEY] = st
    session.modified = True


@bp.get("/spelling-lab")
@login_required
def spelling_lab_page():
    return render_template("spelling_lab.html", title="Spelling Lab")


@bp.post("/api/spelling-lab/start")
@login_required
def api_spelling_start():
    if not request.is_json:
        return jsonify(error="expected json"), 400
    body = request.get_json(silent=True) or {}
    mode = (body.get("mode") or "").strip().lower()
    if mode not in {"flash", "scramble", "gaps", "sprint"}:
        return jsonify(error="mode must be flash, scramble, gaps, or sprint"), 400
    words = load_word_list()
    if not words:
        return jsonify(error="no words — add spelling_custom_words.txt or vocabulary words"), 400

    st: dict[str, Any] = {
        "mode": mode,
        "seed": random.randint(1, 2**31 - 1),
        "i": 0,
        "score": 0,
        "streak": 0,
        "best": 0,
        "limit": float(SPRINT_START_SEC),
        "active": None,
    }
    _save_state(st)
    pool = shuffled_pool(st["seed"])
    return jsonify(ok=True, total=len(pool), mode=mode)


@bp.get("/api/spelling-lab/challenge")
@login_required
def api_spelling_challenge():
    st = _state()
    if not st:
        return jsonify(error="start a game first"), 400

    pool = shuffled_pool(int(st["seed"]))
    i = int(st["i"])
    mode = str(st["mode"])

    if i >= len(pool):
        return jsonify(
            done=True,
            mode=mode,
            total=len(pool),
            score=int(st["score"]),
            streak=int(st["streak"]),
            best=int(st["best"]),
        )

    word = pool[i]
    now = time.time()

    if mode == "flash":
        deadline = now + _ANSWER_SLACK_SEC
        st["active"] = {"word": word, "deadline": deadline}
        _save_state(st)
        return jsonify(
            done=False,
            kind="flash",
            index=i + 1,
            total=len(pool),
            word=word,
            flash_ms=int(FLASH_SHOW_SEC * 1000),
            deadline=deadline,
        )

    if mode == "scramble":
        scrambled = scramble_letters(word)
        deadline = now + _ANSWER_SLACK_SEC
        st["active"] = {"word": word, "deadline": deadline}
        _save_state(st)
        return jsonify(
            done=False,
            kind="scramble",
            index=i + 1,
            total=len(pool),
            scrambled=scrambled.upper(),
            deadline=deadline,
        )

    if mode == "gaps":
        skeleton = make_skeleton(word)
        deadline = now + _ANSWER_SLACK_SEC
        st["active"] = {"word": word, "deadline": deadline}
        _save_state(st)
        return jsonify(
            done=False,
            kind="gaps",
            index=i + 1,
            total=len(pool),
            skeleton=skeleton,
            deadline=deadline,
        )

    if mode == "sprint":
        limit = max(SPRINT_MIN_SEC, float(st["limit"]))
        # Slack includes flash + typing + network delay.
        deadline = now + float(FLASH_SHOW_SEC) + limit + 15.0
        st["active"] = {"word": word, "deadline": deadline}
        _save_state(st)
        return jsonify(
            done=False,
            kind="sprint",
            index=i + 1,
            total=len(pool),
            word=word,
            flash_ms=int(FLASH_SHOW_SEC * 1000),
            type_limit_sec=round(limit, 2),
            min_limit_sec=float(SPRINT_MIN_SEC),
            deadline=deadline,
        )

    return jsonify(error="bad mode"), 400


@bp.post("/api/spelling-lab/answer")
@login_required
def api_spelling_answer():
    if not request.is_json:
        return jsonify(error="expected json"), 400
    st = _state()
    if not st or not st.get("active"):
        return jsonify(error="no active challenge — refresh challenge"), 400

    body = request.get_json(silent=True) or {}
    guess = str(body.get("guess") or "").strip().lower()
    active = st["active"]
    word = str(active["word"])
    deadline = float(active["deadline"])
    mode = str(st["mode"])
    i = int(st["i"])

    if not guess:
        return jsonify(error="empty guess"), 400

    ok_spell = guess == word.lower()
    timed_out = time.time() > deadline and mode == "sprint"

    # Scramble & gaps: stay on the same word until correct (match desktop lab).
    if mode in ("scramble", "gaps"):
        if ok_spell:
            st["score"] = int(st["score"]) + 1
            st["i"] = i + 1
            st["active"] = None
            _save_state(st)
            return jsonify(ok=True, correct=True, answer=word, score=int(st["score"]))
        _save_state(st)
        return jsonify(ok=True, correct=False, try_again=True)

    st["active"] = None

    if mode == "flash":
        correct = ok_spell
        if correct:
            st["streak"] = int(st["streak"]) + 1
            st["best"] = max(int(st["best"]), int(st["streak"]))
        else:
            st["streak"] = 0
        st["i"] = i + 1
        _save_state(st)
        return jsonify(
            ok=True,
            correct=correct,
            answer=word,
            streak=int(st["streak"]),
            best=int(st["best"]),
        )

    if mode == "sprint":
        correct = ok_spell and not timed_out
        if timed_out:
            pass
        elif ok_spell:
            st["score"] = int(st["score"]) + 1
        st["limit"] = max(SPRINT_MIN_SEC, float(st["limit"]) - float(SPRINT_STEP_SEC))
        st["i"] = i + 1
        _save_state(st)
        return jsonify(
            ok=True,
            correct=correct,
            answer=word,
            score=int(st["score"]),
            timed_out=timed_out,
            next_limit=round(float(st["limit"]), 2),
        )

    return jsonify(error="bad mode"), 400
