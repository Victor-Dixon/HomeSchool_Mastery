"""
tutor.py — AI Explanation Engine
Calls Ollama via HTTP API (no subprocess).
Supports two modes:
  - explain()      : Quiz mode — wrong answer on a known question
  - ask_freeform() : Homework mode — parent pastes any question + student answer
"""

import requests
import os

MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
TIMEOUT = 45  # seconds


def _call_ollama(prompt: str) -> str:
    """Send a prompt to Ollama and return the response text."""
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return "Can't reach Ollama. Make sure it's running: `ollama serve`"
    except requests.exceptions.Timeout:
        return "AI took too long. Try again in a moment."
    except Exception as e:
        return f"AI error: {str(e)}"


def explain(skill: str, question: str, user_answer: str, correct_answer: str) -> str:
    """
    Quiz mode: explain a wrong answer on a structured TEKS question.
    Called automatically during !quiz and !drill sessions.
    """
    prompt = f"""
You are a friendly, encouraging 7th grade math tutor.

Skill: {skill}
Question: {question}
Student's Answer: {user_answer}
Correct Answer: {correct_answer}

Do the following:
1. Kindly tell them their answer was not quite right.
2. Show the correct steps clearly and simply.
3. Give one similar practice problem to try.

Keep it under 150 words. Encouraging, simple, easy to read on a phone.
"""
    result = _call_ollama(prompt)
    return result if result else "I couldn't generate an explanation. Try again!"


def ask_freeform(question: str, user_answer: str = "", correct_answer: str = None) -> str:
    """
    Homework mode: supports either:
      1) question + student answer (Discord flow), or
      2) question only (dashboard flow).
    correct_answer is optional — if not provided, the AI figures it out.
    Called by the !ask Discord command.
    """
    user_answer = (user_answer or "").strip()

    if not user_answer:
        prompt = f"""
You are a helpful, encouraging math tutor for a middle school student.

Question: {question}

1. Solve the problem clearly step by step.
2. Explain each step simply.
3. State the final answer clearly.
4. End with one similar practice problem.

Keep it short (under 200 words) and kid-friendly.
"""
    elif correct_answer:
        prompt = f"""
You are a helpful, encouraging math tutor for a middle school student.

Question: {question}
Student's Answer: {user_answer}
Correct Answer: {correct_answer}

1. Explain simply why the student's answer is wrong.
2. Show the correct step-by-step solution.
3. State the final answer clearly.

Keep it short (under 200 words) and kid-friendly.
"""
    else:
        prompt = f"""
You are a helpful, encouraging math tutor for a middle school student.

Question: {question}
Student's Answer: {user_answer}

1. Determine the correct answer to the question.
2. Explain if the student's answer is right or wrong.
3. If wrong, show the correct step-by-step solution clearly.
4. State the final correct answer.

Keep it short (under 200 words) and kid-friendly.
"""
    result = _call_ollama(prompt)
    return result if result else "I couldn't generate an explanation. Try again!"
