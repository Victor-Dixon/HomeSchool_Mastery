"""
Ollama-based grading for Story Duel (and vocabulary blueprint) short answers.

Uses /api/chat with JSON output. On failure, callers should fall back to heuristics.

Model selection (same stack as the lesson AI coach):
  - ``OLLAMA_MODEL`` — defaults to ``gemma3`` if unset (change to llama3.2, mistral, etc.).
  - ``OLLAMA_HOST`` — defaults to ``http://127.0.0.1:11434`` (local Ollama).
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

DEFAULT_MODEL = "gemma3"
DEFAULT_HOST = "http://127.0.0.1:11434"
TIMEOUT_SEC = 55

_SYSTEM = """You are a fair grader for students in grades 4–9.
You receive a passage (or word bank), a question, an optional rubric, and the student's short answer.
Decide if the answer shows reasonable understanding. Accept imperfect spelling and paraphrases.
Reject answers that are off-topic, contradict the passage, or show no real attempt (e.g. one nonsense word).

Respond with ONLY a single JSON object, no markdown, no code fences:
{"valid": true or false, "reason": "one short sentence for the student"}"""


def _extract_json_object(text: str) -> dict[str, Any] | None:
    text = (text or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    return None


def ollama_grade_short_answer(
    *,
    passage: str,
    round_title: str,
    prompt: str,
    student_answer: str,
    rubric: str | None = None,
) -> tuple[bool | None, str]:
    """
    Ask Ollama whether the answer is valid.

    Returns:
        (True/False, reason) on success,
        (None, "") if the model could not be reached or JSON was invalid.
    """
    if len((student_answer or "").strip()) < 3:
        return False, "Answer too short to grade."

    model = (os.environ.get("OLLAMA_MODEL") or DEFAULT_MODEL).strip()
    host = (os.environ.get("OLLAMA_HOST") or DEFAULT_HOST).rstrip("/")
    url = f"{host}/api/chat"

    user_parts = [
        f"Passage or word bank:\n{passage.strip()}",
        f"Round: {round_title}",
        f"Question:\n{prompt.strip()}",
        f"Student answer:\n{student_answer.strip()}",
    ]
    if rubric:
        user_parts.append(f"Grading rubric (follow closely):\n{rubric.strip()}")
    user_msg = "\n\n".join(user_parts)

    body = {
        "model": model,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": user_msg},
        ],
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            raw = json.loads(resp.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, json.JSONDecodeError):
        return None, ""

    msg = (raw.get("message") or {}) if isinstance(raw, dict) else {}
    content = msg.get("content") if isinstance(msg, dict) else None
    if not isinstance(content, str):
        return None, ""

    parsed = _extract_json_object(content)
    if not isinstance(parsed, dict):
        return None, ""

    valid = parsed.get("valid")
    if isinstance(valid, str):
        valid = valid.strip().lower() in ("true", "yes", "1")
    elif not isinstance(valid, bool):
        return None, ""

    reason = str(parsed.get("reason") or "").strip()
    if len(reason) > 280:
        reason = reason[:277] + "…"

    return valid, reason
