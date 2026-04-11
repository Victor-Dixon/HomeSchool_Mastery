"""
Load Story Duel / vocabulary duel bundles from JSON (swappable content).

Blueprint: same JSON schema supports reading rounds and vocabulary-style rounds;
grading is shared (Ollama + heuristic) via story_duel.py.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from .story_duel_schema import BundleValidationError, validate_story_bundle

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parent / "data" / "story_duel"

# Used only when JSON files are missing or invalid (partial deploy, corrupt file).
_EMERGENCY_MARCUS_JSON = """
{
  "id": "marcus_wallet_v1",
  "version": "1.0",
  "kind": "story_duel",
  "title": "Story Duel — Marcus & the wallet",
  "grading": "auto",
  "passage": "Marcus found a wallet on the ground. No one was around. He looked inside and saw money and an ID. He paused, then walked toward the office.",
  "rounds": [
    {
      "id": "main_idea",
      "kind": "comprehension",
      "title": "Main Idea Strike",
      "prompt": "What is the main idea of the passage?",
      "rubric": "Valid if the student states that Marcus finds a wallet and is deciding what to do, or is going to return it.",
      "keywords": ["wallet", "marcus", "office", "return"],
      "min_keyword_hits": 2
    }
  ]
}
"""


def _registry() -> dict[str, Any]:
    p = _DATA_DIR / "registry.json"
    if not p.is_file():
        return {"default": "marcus_wallet_v1"}
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def get_default_bundle_id() -> str:
    rid = (os.environ.get("STORY_DUEL_BUNDLE_ID") or "").strip()
    if rid:
        return rid
    return str(_registry().get("default") or "marcus_wallet_v1")


def _emergency_bundle() -> dict[str, Any]:
    data = json.loads(_EMERGENCY_MARCUS_JSON)
    validate_story_bundle(data, source_name="emergency_builtin")
    return data


def load_story_bundle(bundle_id: str | None) -> dict[str, Any]:
    """
    Load ``{bundle_id}.json`` from app/data/story_duel/.
    Falls back to registry default if missing.
    If files are missing or invalid (partial install), returns a small built-in bundle so routes do not 500.
    """
    bid = (bundle_id or "").strip() or get_default_bundle_id()
    path = _DATA_DIR / f"{bid}.json"
    tried: list[Path] = []
    if not path.is_file():
        tried.append(path)
        fallback = str(_registry().get("default") or "marcus_wallet_v1")
        path = _DATA_DIR / f"{fallback}.json"
    if not path.is_file():
        tried.append(path)
        logger.warning(
            "Story duel JSON not found (tried %s); using built-in emergency bundle.",
            ", ".join(str(p) for p in tried) if tried else str(path),
        )
        return _emergency_bundle()
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Story duel JSON unreadable (%s): %s; using emergency bundle.", path, exc)
        return _emergency_bundle()
    if "id" not in data:
        data["id"] = bid
    try:
        validate_story_bundle(data, source_name=path.name)
    except BundleValidationError as exc:
        logger.warning("Story duel bundle invalid (%s): %s; using emergency bundle.", path, exc)
        return _emergency_bundle()
    return data


def bundle_id_from_lesson_notes(notes: str | None) -> str | None:
    """Match ``story_duel_bundle:storm_library_v1`` (or hyphenated slug) in lesson notes."""
    if not notes:
        return None
    m = re.search(r"story_duel_bundle:\s*([a-z0-9_\-]+)", notes, flags=re.IGNORECASE)
    return m.group(1).strip().lower() if m else None
