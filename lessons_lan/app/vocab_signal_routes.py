"""
Vocabulary Signal Breaker — repurposed Signal Breaker UI using vocabulary_game.WORDS.
"""

from __future__ import annotations

import json

from flask import Blueprint, render_template

from vocabulary_game import SENTENCES, WORDS

from .auth import login_required

bp = Blueprint("vocab_signal", __name__)


@bp.get("/games/vocabulary-signal-breaker")
@login_required
def vocabulary_signal_breaker():
    vocab_list = [
        {"word": w, "definition": WORDS[w], "sentence": SENTENCES.get(w, "")}
        for w in WORDS
    ]
    return render_template(
        "vocabulary_signal_breaker.html",
        title="Vocabulary Signal Breaker",
        vocab_json=json.dumps(vocab_list),
    )
