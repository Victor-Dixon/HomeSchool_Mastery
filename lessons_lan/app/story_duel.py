"""
Project: Homeschool Lessons (Dream.OS)
File: app/story_duel.py
Purpose: Story Duel — swappable JSON bundles, Ollama grading with heuristic fallback (vocab blueprint compatible).
"""

from __future__ import annotations

import os
from typing import Any

from itsdangerous import BadSignature, URLSafeSerializer

from .grading import normalize_text
from .story_duel_llm import ollama_grade_short_answer

# Signed payload the browser echoes on each round (avoids Flask session cookie limits / drops).
_DUEL_STATE_SALT = "homeschool-story-duel-state-v1"

FAST_ANSWER_MS = 10_000
DAMAGE_FAST_CORRECT = 20
DAMAGE_SLOW_CORRECT = 10
DAMAGE_WRONG_PLAYER = 15


def round_is_correct(answer: str, spec: dict[str, Any]) -> bool:
    """Keyword / substring heuristic (offline fallback). Validated bundles use substring_hints."""
    a = normalize_text(answer)
    if len(a) < 2:
        return False

    for s in spec.get("substring_hints") or []:
        if normalize_text(str(s)) in a:
            return True

    if spec.get("kind") == "vocabulary_match":
        for opt in spec.get("answers") or []:
            no = normalize_text(str(opt))
            if no and (no in a or a in no):
                return True

    one_ans = spec.get("answer")
    if one_ans and normalize_text(str(one_ans)) in a:
        return True

    keys = spec.get("keywords") or []
    if keys:
        need = int(spec.get("min_keyword_hits") or 2)
        hits = sum(1 for k in keys if normalize_text(str(k)) in a)
        if hits >= need:
            return True

    return False


def _effective_grading_mode(spec: dict[str, Any], bundle: dict[str, Any]) -> str:
    g = (spec.get("grading") or bundle.get("grading") or "auto").strip().lower()
    if g in ("heuristic_only", "heuristic"):
        return "heuristic_only"
    if g in ("ollama_only", "ollama"):
        return "ollama_only"
    return "auto"


def _ollama_strict() -> bool:
    return os.environ.get("STORY_DUEL_OLLAMA_STRICT", "").strip().lower() in ("1", "true", "yes")


def grade_round_answer(
    *,
    answer: str,
    spec: dict[str, Any],
    passage: str,
    bundle: dict[str, Any],
) -> tuple[bool, str, str]:
    """
    Returns (correct, source, feedback).

    source: "ollama" | "heuristic" | "ollama_offline"
    feedback: short coach sentence when Ollama supplied one
    """
    mode = _effective_grading_mode(spec, bundle)
    rubric = spec.get("rubric")
    rubric_s = str(rubric).strip() if rubric else None
    title = str(spec.get("title") or "Round")
    prompt = str(spec.get("prompt") or "")

    def heuristic() -> tuple[bool, str, str]:
        ok = round_is_correct(answer, spec)
        return ok, "heuristic", ""

    if mode == "heuristic_only":
        return heuristic()

    if mode == "ollama_only":
        llm_ok, reason = ollama_grade_short_answer(
            passage=passage,
            round_title=title,
            prompt=prompt,
            student_answer=answer,
            rubric=rubric_s,
        )
        if llm_ok is not None:
            return bool(llm_ok), "ollama", reason
        if _ollama_strict():
            return False, "ollama_offline", (
                "Reading coach (Ollama) is not reachable — answer counted as a miss. "
                "Ask a parent to start Ollama, or turn off strict mode."
            )
        return heuristic()

    # auto: Ollama first, then heuristic
    llm_ok, reason = ollama_grade_short_answer(
        passage=passage,
        round_title=title,
        prompt=prompt,
        student_answer=answer,
        rubric=rubric_s,
    )
    if llm_ok is not None:
        return bool(llm_ok), "ollama", reason
    ok, _, _ = heuristic()
    return ok, "heuristic", ""


def serialize_bundle_public(bundle: dict[str, Any]) -> dict[str, Any]:
    """Strip grading hints for the browser."""
    rounds_out = []
    for r in bundle["rounds"]:
        rounds_out.append(
            {
                "id": r["id"],
                "kind": r.get("kind") or "",
                "title": r.get("title") or r["id"],
                "prompt": r["prompt"],
            }
        )
    return {
        "bundle_id": bundle["id"],
        "title": bundle["title"],
        "subtitle": bundle.get("subtitle") or "",
        "read_phase_seconds": bundle.get("read_phase_seconds") or 18,
        "passage": bundle["passage"],
        "opponent_name": bundle.get("opponent_name") or "Rival reader",
        "rounds": rounds_out,
    }


def initial_state(*, bundle_id: str, user_id: int) -> dict[str, Any]:
    return {
        "uid": int(user_id),
        "player_hp": 100,
        "ai_hp": 100,
        "round_idx": 0,
        "streak": 0,
        "done": False,
        "outcome": None,
        "bundle_id": bundle_id,
        "xp_awarded": False,
    }


def encode_duel_state(secret: str, state: dict[str, Any]) -> str:
    """HMAC-signed duel state for client round-trips (no server session required)."""
    ser = URLSafeSerializer(secret, salt=_DUEL_STATE_SALT)
    return ser.dumps(state)


def decode_duel_state(secret: str, token: str) -> dict[str, Any] | None:
    ser = URLSafeSerializer(secret, salt=_DUEL_STATE_SALT)
    try:
        raw = ser.loads(token)
    except BadSignature:
        return None
    if not isinstance(raw, dict):
        return None
    return raw


def coerce_duel_state(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Validate minimal shape after decode; return None if unusable."""
    try:
        uid = int(raw["uid"])
        bid = str(raw["bundle_id"] or "").strip()
        if not bid:
            return None
        return {
            "uid": uid,
            "bundle_id": bid,
            "player_hp": int(raw.get("player_hp", 100)),
            "ai_hp": int(raw.get("ai_hp", 100)),
            "round_idx": int(raw.get("round_idx", 0)),
            "streak": int(raw.get("streak", 0)),
            "done": bool(raw.get("done")),
            "outcome": raw.get("outcome"),
            "xp_awarded": bool(raw.get("xp_awarded")),
        }
    except (KeyError, TypeError, ValueError):
        return None


def apply_round(
    *,
    answer: str,
    ms_elapsed: int,
    bundle: dict[str, Any],
    state: dict[str, Any],
) -> dict[str, Any]:
    rounds = bundle["rounds"]
    idx = int(state["round_idx"])
    spec = rounds[idx]
    passage = str(bundle.get("passage") or "")

    ok, source, feedback = grade_round_answer(answer=answer, spec=spec, passage=passage, bundle=bundle)

    player_hp = int(state["player_hp"])
    ai_hp = int(state["ai_hp"])
    streak = int(state["streak"])
    narrative_parts: list[str] = []

    if ok:
        base = DAMAGE_FAST_CORRECT if ms_elapsed <= FAST_ANSWER_MS else DAMAGE_SLOW_CORRECT
        mult = 1.0 + 0.1 * min(streak, 5)
        dmg = int(base * mult)
        ai_hp = max(0, ai_hp - dmg)
        streak += 1
        speed = "fast" if ms_elapsed <= FAST_ANSWER_MS else "slow"
        narrative_parts.append(
            f"{spec['title']} hits for {dmg} ({speed} correct answer, combo x{mult:.1f})."
        )
        if source == "ollama" and feedback:
            narrative_parts.append(f"Coach: {feedback}")
        elif source == "heuristic":
            narrative_parts.append("(Keyword backup — start Ollama for smarter grading.)")
    else:
        player_hp = max(0, player_hp - DAMAGE_WRONG_PLAYER)
        streak = 0
        narrative_parts.append(f"{bundle.get('opponent_name', 'Opponent')} counterattacks for {DAMAGE_WRONG_PLAYER}.")
        if feedback:
            narrative_parts.append(f"Coach: {feedback}")
        if source == "heuristic" and not feedback:
            narrative_parts.append("Tip: add evidence from the passage or try synonyms of the main idea.")

    state["player_hp"] = player_hp
    state["ai_hp"] = ai_hp
    state["streak"] = streak

    battle_end = None
    if player_hp <= 0:
        state["done"] = True
        state["outcome"] = "lose"
        battle_end = "lose"
        narrative_parts.append("You are overwhelmed — study the passage and try again.")
    elif ai_hp <= 0:
        state["done"] = True
        state["outcome"] = "win"
        battle_end = "win"
        narrative_parts.append("Opponent fades into the Fog. Victory!")
    else:
        state["round_idx"] = idx + 1
        if state["round_idx"] >= len(rounds):
            if ai_hp < player_hp:
                state["done"] = True
                state["outcome"] = "win"
                battle_end = "win"
                narrative_parts.append("Last exchange — you had the stronger read!")
            else:
                state["done"] = True
                state["outcome"] = "lose"
                battle_end = "lose"
                narrative_parts.append("Time — the Fog Reader edges you out.")

    next_round: dict[str, Any] | None = None
    if battle_end is None and not state.get("done"):
        nidx = int(state["round_idx"])
        if 0 <= nidx < len(rounds):
            nr = rounds[nidx]
            next_round = {"id": nr["id"], "kind": nr.get("kind") or "", "title": nr["title"], "prompt": nr["prompt"]}

    return {
        "correct": ok,
        "player_hp": player_hp,
        "ai_hp": ai_hp,
        "streak": streak,
        "round_index": idx,
        "narrative": " ".join(narrative_parts),
        "battle_end": battle_end,
        "next_round": next_round,
        "grading_source": source,
        "grading_feedback": feedback,
    }


def xp_for_outcome(outcome: str | None) -> int:
    if outcome == "win":
        return 35
    if outcome == "lose":
        return 10
    return 0
