"""
Discount Dash — timed percent-off problems, coins/HP duel, method bonus XP.
"""

from __future__ import annotations

import json
import random
from typing import Any


def session_key(lesson_id: int | None, user_id: int) -> str:
    return f"discdash_{lesson_id if lesson_id is not None else 'demo'}_{user_id}"


def _get(sess: Any, key: str) -> dict[str, Any] | None:
    raw = sess.get(key)
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def _put(sess: Any, key: str, data: dict[str, Any]) -> None:
    sess[key] = data
    sess.modified = True


get_dash_state = _get
set_dash_state = _put


def random_item() -> dict[str, Any]:
    price = random.choice([10, 12, 15, 18, 20, 24, 30, 36, 40, 45])
    pct = random.choice([10, 15, 20, 25, 30, 40, 50])
    exact = price * (100 - pct) / 100.0
    if abs(exact - round(exact)) < 1e-6:
        ans = float(int(round(exact)))
    else:
        ans = round(exact, 2)
    return {"price": price, "discount_pct": pct, "answer": ans}


def initial_state(*, rounds_total: int = 5) -> dict[str, Any]:
    first = random_item()
    return {
        "player_hp": 100,
        "ai_hp": 100,
        "streak": 0,
        "round_idx": 0,
        "rounds_total": rounds_total,
        "current": first,
        "phase": "shop",
        "done": False,
        "outcome": None,
        "xp_bank": 0,
        "method_xp_awarded": False,
    }


def _speed_mult(ms: int) -> float:
    return max(0.48, 1.0 - min(ms, 12000) / 24000.0)


def _close_enough(student: float, target: float) -> bool:
    return abs(student - target) <= 0.051 + 1e-6


def process_answer(*, state: dict[str, Any], raw_answer: Any, ms: int) -> tuple[dict[str, Any], int]:
    if state.get("done"):
        return ({"error": "round over"}, 400)
    try:
        student = float(str(raw_answer).strip().replace("$", "").replace(",", ""))
    except (TypeError, ValueError):
        student = -1e9
    cur = state["current"]
    target = float(cur["answer"])
    ok = _close_enough(student, target)
    ms = max(0, int(ms))

    sp = _speed_mult(ms)
    combo = 1.0 + 0.1 * min(int(state["streak"]), 5)
    xp_this = 0
    line = ""

    if ok:
        dmg = int(18 * sp * combo)
        dmg = max(6, dmg)
        state["ai_hp"] = max(0, int(state["ai_hp"]) - dmg)
        state["streak"] = int(state["streak"]) + 1
        line = f"Correct sale price — price bomb for {dmg}. 💥"
        xp_this = 8 + (4 if sp >= 0.85 else 0)
    else:
        bruise = 14
        state["player_hp"] = max(0, int(state["player_hp"]) - bruise)
        state["streak"] = 0
        line = f"Wrong — rival shopper steals {bruise} coins. (Target: {target})"

    state["xp_bank"] = int(state.get("xp_bank") or 0) + xp_this
    state["round_idx"] = int(state["round_idx"]) + 1
    ri = int(state["round_idx"])
    total = int(state["rounds_total"])
    php = int(state["player_hp"])
    ahp = int(state["ai_hp"])

    done = False
    outcome = None
    if php <= 0:
        done = True
        outcome = "lose"
    elif ahp <= 0:
        done = True
        outcome = "win"
    elif ri >= total:
        done = True
        if php > ahp:
            outcome = "win"
        elif ahp > php:
            outcome = "lose"
        else:
            outcome = "win" if int(state.get("streak") or 0) > 0 else "lose"

    next_item = None
    if not done:
        next_item = random_item()
        state["current"] = next_item
    else:
        state["phase"] = "method"
        state["done"] = True
        state["outcome"] = outcome
        bump = 25 if outcome == "win" else 12
        state["xp_bank"] = int(state.get("xp_bank") or 0) + bump
        line += f" Flash sale over — {'you stocked up!' if outcome == 'win' else 'try again.'}"

    return (
        {
            "ok": True,
            "correct": ok,
            "narrative": line,
            "player_hp": php,
            "ai_hp": ahp,
            "streak": int(state["streak"]),
            "round": int(state["round_idx"]),
            "done": done,
            "outcome": outcome,
            "xp_this": xp_this,
            "xp_bank": int(state["xp_bank"]),
            "next_item": next_item,
        },
        200,
    )


def process_method_bonus(*, state: dict[str, Any], method: str) -> tuple[dict[str, Any], int]:
    if not state.get("done"):
        return ({"error": "finish items first"}, 400)
    if state.get("method_xp_awarded"):
        return ({"ok": True, "xp": 0}, 200)
    state["method_xp_awarded"] = True
    m = (method or "").strip().lower()
    xp = 5 if m in ("subtract", "multiply", "subtract_discount", "multiply_remaining") else 3
    state["xp_bank"] = int(state.get("xp_bank") or 0) + xp
    return ({"ok": True, "xp": xp, "xp_bank": int(state["xp_bank"])}, 200)


def public_intro() -> dict[str, Any]:
    return {
        "title": "Discount Dash",
        "tagline": "Real-time price survival — percent tags drop; you strike first with math.",
    }
