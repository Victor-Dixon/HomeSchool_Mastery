"""
Project: Homeschool Lessons (Dream.OS)
File: app/tutor.py
Purpose: Optional Ollama tutor wrapper (fail-safe, no extra deps).
Owner: Local family deployment (homeschool)
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


DEFAULT_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
DEFAULT_OLLAMA_CHAT_URL = os.environ.get("OLLAMA_CHAT_URL", "http://127.0.0.1:11434/api/chat")
DEFAULT_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3")


def ollama_explain_miss(
    question: dict[str, Any],
    student_answer: str,
    *,
    url: str = DEFAULT_OLLAMA_URL,
    model: str = DEFAULT_OLLAMA_MODEL,
    timeout_s: float = 20.0,
) -> str:
    prompt = f"""
You are a calm tutor for a homeschool student.

Grade: {question.get('grade')}
Subject: {question.get('subject')}
Skill: {question.get('skill')}
TEKS: {', '.join(question.get('teks_tags') or [])}

Question:
{question.get('prompt')}

Student answer:
{student_answer}

Correct answer:
{question.get('correct_answer')}

Explain briefly:
1. Why the answer was incorrect
2. How to solve it correctly
3. Give one tip to remember next time

Keep it short and child-friendly.
""".strip()

    payload = {"model": model, "prompt": prompt, "stream": False}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        data = json.loads(body or "{}")
        text = (data.get("response") or "").strip()
        return text or "Let's try that skill again step by step."
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError):
        return "Let's try that skill again step by step."


def ollama_chat(
    messages: list[dict[str, str]],
    *,
    url: str | None = None,
    model: str | None = None,
    timeout_s: float = 120.0,
) -> tuple[str, bool]:
    """
    Multi-turn chat via Ollama /api/chat.
    messages: [{"role":"system"|"user"|"assistant","content":"..."}, ...]
    Returns (assistant_text, success). On failure, assistant_text is a kid-friendly offline hint.
    """
    url = url or DEFAULT_OLLAMA_CHAT_URL
    model = model or DEFAULT_OLLAMA_MODEL
    payload: dict[str, Any] = {"model": model, "messages": messages, "stream": False}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        data = json.loads(body or "{}")
        msg = data.get("message") or {}
        text = (msg.get("content") or "").strip()
        if not text:
            return ("The AI didn’t answer. Try a shorter question or check that a model is pulled in Ollama.", False)
        return (text, True)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError):
        return (
            "AI lesson coach is offline. Ask a parent to run **Ollama** on this computer (`ollama serve`), "
            "then try again. You can still use **Practice** below.",
            False,
        )


def build_lesson_system_prompt(
    *,
    title: str,
    subject: str,
    grade: int | None,
    display_name: str,
    notes: str,
) -> str:
    if grade is not None:
        try:
            gi = int(grade)
            grade_bit = f"grade {gi}" if gi > 0 else "their level"
        except (TypeError, ValueError):
            grade_bit = "their level"
    else:
        grade_bit = "their level"
    notes = (notes or "").strip() or "(No extra notes — answer from title and subject only.)"
    return f"""You are a warm, patient homeschool tutor helping {display_name} (about {grade_bit}).

STRICT RULES:
- Teach using ONLY the LESSON MATERIAL below. Do not invent new problems, facts, or assignments unless they are obvious follow-ups from that material.
- Short, clear chunks. Encourage the student. Never shame.
- If they go off-topic, gently steer back to this lesson.
- If something isn’t in the material, say you’re not sure and point them to the lesson text or Practice.

LESSON TITLE: {title}
SUBJECT: {subject}

LESSON MATERIAL:
---
{notes}
---
""".strip()
