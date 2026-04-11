"""
Shared spelling helpers (GUI + web). Word list: vocabulary_game + spelling_custom_words.txt.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import List

from vocabulary_game import WORDS

_CUSTOM_FILE = Path(__file__).resolve().parent / "spelling_custom_words.txt"

SPRINT_START_SEC = 18.0
SPRINT_MIN_SEC = 3.0
SPRINT_STEP_SEC = 1.0
FLASH_SHOW_SEC = 2.0


def _normalize_line(line: str) -> str | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    return line


def load_word_list() -> List[str]:
    """Default vocab words plus optional custom file; dedupe case-insensitively."""
    seen: set[str] = set()
    out: List[str] = []
    for w in WORDS:
        lw = w.lower()
        if lw not in seen:
            seen.add(lw)
            out.append(w)
    if _CUSTOM_FILE.is_file():
        try:
            text = _CUSTOM_FILE.read_text(encoding="utf-8")
        except OSError:
            text = ""
        for line in text.splitlines():
            w = _normalize_line(line)
            if not w:
                continue
            lw = w.lower()
            if lw not in seen:
                seen.add(lw)
                out.append(w)
    return out


def save_custom_words(lines: List[str]) -> None:
    body = "\n".join(lines) + ("\n" if lines else "")
    _CUSTOM_FILE.write_text(body, encoding="utf-8")


def scramble_letters(word: str) -> str:
    letters = list(word)
    if len(letters) <= 1:
        return word
    for _ in range(12):
        random.shuffle(letters)
        cand = "".join(letters)
        if cand.lower() != word.lower():
            return cand
    return "".join(letters)


def make_skeleton(word: str) -> str:
    """Hide ~half the letters (at least one shown if len > 1)."""
    w = word
    alpha_idx = [i for i, c in enumerate(w) if c.isalpha()]
    if len(alpha_idx) <= 1:
        return w
    n_hide = max(1, len(alpha_idx) // 2)
    n_hide = min(n_hide, len(alpha_idx) - 1)
    hide = set(random.sample(alpha_idx, n_hide))
    chars: List[str] = []
    for i, c in enumerate(w):
        if i in hide:
            chars.append("_")
        else:
            chars.append(c)
    return "".join(chars)


def shuffled_pool(seed: int) -> List[str]:
    """Deterministic shuffle for server session (same seed → same order)."""
    words = load_word_list()
    rng = random.Random(seed)
    pool = words[:]
    rng.shuffle(pool)
    return pool
