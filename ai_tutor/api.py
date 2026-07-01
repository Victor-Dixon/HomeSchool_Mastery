"""
api.py — Flask API Server
The "brain" — Discord bot calls this, but so can a web app, mobile app, or Zapier.

Endpoints:
  POST /ask     — Free-form homework question (parent pastes anything)
  POST /explain — Structured quiz explanation (question + wrong answer + correct answer)
  GET  /health  — Check if server is up

Run with:
  python -m ai_tutor.api

Or in production:
  gunicorn ai_tutor.api:app --bind 0.0.0.0:5000
"""

from flask import Flask, request, jsonify
from ai_tutor import tutor
import os

app = Flask(__name__)
API_KEY = os.getenv("API_KEY", "")


def _check_auth():
    """If API_KEY is set in .env, require it in the X-API-Key header."""
    if API_KEY:
        key = request.headers.get("X-API-Key", "")
        if key != API_KEY:
            return False
    return True


@app.route("/health", methods=["GET"])
def health():
    """Quick check to confirm the API is running."""
    return jsonify({"status": "ok", "model": os.getenv("OLLAMA_MODEL", "llama3")})


@app.route("/ask", methods=["POST"])
def ask():
    """
    Free-form homework help.
    Body (JSON):
      question        — The homework problem (required)
      user_answer     — What the student answered (optional)
      correct_answer  — The right answer (optional — AI will figure it out if omitted)

    Minimal example:
      { "question": "3/4 + 1/2" }
    """
    if not _check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    question = data.get("question", "").strip()
    user_answer = data.get("user_answer", "").strip()
    correct_answer = data.get("correct_answer", "").strip() or None

    if not question:
        return jsonify({"error": "Field 'question' is required"}), 400

    explanation = tutor.ask_freeform(question, user_answer, correct_answer)
    return jsonify({"explanation": explanation})


@app.route("/explain", methods=["POST"])
def explain():
    """
    Structured quiz explanation (used internally by the Discord quiz commands).
    Body (JSON):
      skill           — TEKS skill name
      question        — The question text
      user_answer     — Student's wrong answer
      correct_answer  — The right answer
    """
    if not _check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    skill = data.get("skill", "Math").strip()
    question = data.get("question", "").strip()
    user_answer = data.get("user_answer", "").strip()
    correct_answer = data.get("correct_answer", "").strip()

    if not question or not user_answer or not correct_answer:
        return jsonify({"error": "Fields 'question', 'user_answer', and 'correct_answer' are required"}), 400

    explanation = tutor.explain(skill, question, user_answer, correct_answer)
    return jsonify({"explanation": explanation})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Tutor API running on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
