"""
Text Detective: Case Battle — passage, purpose, structure, evidence picks, reflection XP.
"""

from __future__ import annotations

import json
from typing import Any

from .grading import normalize_text


def session_key(lesson_id: int | None, user_id: int) -> str:
    return f"txdet_{lesson_id if lesson_id is not None else 'demo'}_{user_id}"


def detective_client_bundle() -> dict[str, Any]:
    """Safe for the browser — no answer keys."""
    b = public_bundle()
    out: dict[str, Any] = {
        "title": b["title"],
        "read_seconds": b["read_seconds"],
        "passage": b["passage"],
        "reflection_prompt": b["reflection_prompt"],
        "rounds": [],
    }
    for r in b["rounds"]:
        entry: dict[str, Any] = {
            "id": r["id"],
            "kind": r["kind"],
            "title": r["title"],
            "prompt": r["prompt"],
            "input": r["input"],
        }
        if r["input"] == "mcq":
            entry["choices"] = [{"value": c["value"], "label": c["label"]} for c in r["choices"]]
        else:
            entry["snippets"] = [{"id": s["id"], "text": s["text"]} for s in r["snippets"]]
        out["rounds"].append(entry)
    return out


def public_bundle() -> dict[str, Any]:
    return {
        "title": "Text Detective: Case Battle",
        "read_seconds": 16,
        "passage": (
            "The author describes a storm as “angry and alive,” shaking the town with force."
        ),
        "reflection_prompt": "How did vivid verbs and adjectives change the mood?",
        "rounds": [
            {
                "id": "purpose",
                "kind": "purpose_probe",
                "title": "Purpose Probe",
                "prompt": "What is the author’s primary purpose in this description?",
                "input": "mcq",
                "choices": [
                    {"value": "describe", "label": "Describe / create a picture or mood"},
                    {"value": "persuade", "label": "Persuade the reader"},
                    {"value": "inform", "label": "Inform with facts only"},
                    {"value": "entertain", "label": "Entertain with humor or story"},
                ],
                "answer": "describe",
            },
            {
                "id": "structure",
                "kind": "structure_scan",
                "title": "Structure Scan",
                "prompt": "What text structure is used here?",
                "input": "mcq",
                "choices": [
                    {"value": "description", "label": "Description"},
                    {"value": "cause_effect", "label": "Cause and effect"},
                    {"value": "problem_solution", "label": "Problem and solution"},
                    {"value": "sequence", "label": "Sequence / chronological order"},
                ],
                "answer": "description",
            },
            {
                "id": "evidence",
                "kind": "evidence_lock",
                "title": "Evidence Lock",
                "prompt": "Select the phrases that BEST support a vivid storm mood.",
                "input": "multi_snippets",
                "snippets": [
                    {"id": "s1", "text": "“angry and alive,”"},
                    {"id": "s2", "text": "shaking the town with force"},
                    {"id": "s3", "text": "The author describes a storm"},
                    {"id": "s4", "text": "the town"},
                ],
                "correct_ids": ["s1", "s2"],
            },
        ],
    }


def _get_state(sess: Any, key: str) -> dict[str, Any] | None:
    raw = sess.get(key)
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def _set_state(sess: Any, key: str, data: dict[str, Any]) -> None:
    sess[key] = data
    sess.modified = True


def initial_state() -> dict[str, Any]:
    return {
        "player_hp": 100,
        "ai_hp": 100,
        "round_idx": 0,
        "streak": 0,
        "evidence_mult": 1.0,
        "phase": "live",
        "battle_over": None,
        "xp_total": 0,
        "reflection_xp_awarded": False,
    }


def _speed_mult(ms: int) -> float:
    return max(0.5, 1.0 - min(ms, 28000) / 56000.0)


def process_step(
    *,
    state: dict[str, Any],
    payload: dict[str, Any],
    bundle: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    rounds = bundle["rounds"]
    idx = int(state["round_idx"])
    if idx >= len(rounds):
        return ({"error": "no round"}, 400)
    spec = rounds[idx]
    try:
        ms = int(payload.get("ms_elapsed") or 0)
    except (TypeError, ValueError):
        ms = 0
    ms = max(0, ms)

    correct = False
    evidence_quality = 1.0

    if spec["input"] == "mcq":
        val = normalize_text(str(payload.get("value") or ""))
        ans = normalize_text(str(spec["answer"]))
        correct = val == ans
    elif spec["input"] == "multi_snippets":
        picked = payload.get("picked") or []
        if not isinstance(picked, list):
            picked = []
        picked_set = {str(x) for x in picked}
        need = set(spec["correct_ids"])
        if picked_set == need:
            correct = True
            evidence_quality = 1.15
        elif picked_set & need:
            correct = True
            evidence_quality = 0.75
        else:
            correct = False

    sp = _speed_mult(ms)
    combo = 1.0 + 0.085 * min(int(state["streak"]), 6)
    mult = float(state.get("evidence_mult") or 1.0)

    narrative: list[str] = []
    battle_over = None
    xp_this = 0

    if correct:
        base = 15 if spec["input"] == "mcq" else 18
        if spec["id"] == "evidence":
            base = int(base * evidence_quality)
        dmg = int(base * sp * combo * mult * (evidence_quality if spec["id"] == "evidence" else 1.0))
        dmg = max(4, dmg)
        state["ai_hp"] = max(0, int(state["ai_hp"]) - dmg)
        if spec["input"] == "multi_snippets" and evidence_quality < 1.0:
            state["streak"] = 0
        else:
            state["streak"] = int(state["streak"]) + 1
        narrative.append(f"{spec['title']}: solid case — {dmg} to the rival reader.")
        if spec["id"] == "structure":
            state["evidence_mult"] = 1.28
            narrative.append("Structure scan unlocked an evidence multiplier for your final lock.")
        xp_this = 6 + (3 if sp >= 0.82 else 0)
    else:
        loss = 17
        state["player_hp"] = max(0, int(state["player_hp"]) - loss)
        state["streak"] = 0
        narrative.append(f"{spec['title']}: weak proof — rival hits you for {loss}.")

    state["xp_total"] = int(state.get("xp_total") or 0) + xp_this

    battle_over = None
    php = int(state["player_hp"])
    ahp = int(state["ai_hp"])
    if php <= 0:
        battle_over = "lose"
    elif ahp <= 0:
        battle_over = "win"
    else:
        state["round_idx"] = idx + 1
        if state["round_idx"] >= len(rounds):
            if php > ahp:
                battle_over = "win"
            elif ahp > php:
                battle_over = "lose"
            else:
                battle_over = "win" if int(state.get("streak") or 0) > 0 else "lose"

    if battle_over:
        state["phase"] = "reflection"
        state["battle_over"] = battle_over
        bonus = 22 if battle_over == "win" else 10
        state["xp_total"] = int(state.get("xp_total") or 0) + bonus
        narrative.append("Case closed — add a reflection to seal extra XP.")

    return (
        {
            "ok": True,
            "correct": correct,
            "player_hp": php,
            "ai_hp": ahp,
            "streak": int(state["streak"]),
            "narrative": " ".join(narrative),
            "battle_over": battle_over,
            "phase": state["phase"],
            "xp_this_round": xp_this,
            "xp_total_so_far": int(state["xp_total"]),
            "next_round_index": int(state["round_idx"]) if not battle_over else None,
        },
        200,
    )


def process_reflection(*, state: dict[str, Any], text: str) -> tuple[dict[str, Any], int]:
    if state.get("reflection_xp_awarded"):
        return ({"ok": True, "xp": 0, "message": "Reflection already counted."}, 200)
    state["reflection_xp_awarded"] = True
    note = (text or "").strip()
    bonus = 6 if len(note) >= 12 else 3
    state["xp_total"] = int(state.get("xp_total") or 0) + bonus
    return ({"ok": True, "xp": bonus, "xp_total": int(state["xp_total"]), "message": "Reflection logged."}, 200)


detective_get_state = _get_state
detective_set_state = _set_state
td_initial_state = initial_state
