"""
Strict validation for Story Duel / vocabulary bundle JSON.

Fails fast with file-specific paths (e.g. marcus_wallet_v1.json.rounds[0].kind).
"""

from __future__ import annotations

from typing import Any

ALLOWED_BUNDLE_KINDS = frozenset({"story_duel", "vocabulary"})
ALLOWED_GRADING_MODES = frozenset({"auto", "heuristic_only", "ollama_only"})
ALLOWED_ROUND_KINDS = frozenset(
    {
        "comprehension",
        "inference",
        "vocabulary_define",
        "vocabulary_use",
        "vocabulary_match",
    }
)


class BundleValidationError(ValueError):
    """Raised when a bundle dict fails schema checks."""


def _require_non_empty_string(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise BundleValidationError(f"{field} must be a non-empty string")


def _round_has_grading_input(round_item: dict[str, Any]) -> bool:
    rub = round_item.get("rubric")
    if rub is not None and str(rub).strip():
        return True
    kw = round_item.get("keywords")
    if isinstance(kw, list) and kw and all(isinstance(k, str) and k.strip() for k in kw):
        return True
    ans = round_item.get("answer")
    if ans is not None and str(ans).strip():
        return True
    ans_list = round_item.get("answers")
    if isinstance(ans_list, list) and any(str(a).strip() for a in ans_list):
        return True
    return False


def validate_story_bundle(bundle: dict[str, Any], *, source_name: str = "<bundle>") -> dict[str, Any]:
    """
    Validate and return the same dict (no silent field invention).

    Top-level required: id, title, kind, passage, rounds.
    Each round requires: id, title, prompt (plus grading inputs per rules below).
    """
    if not isinstance(bundle, dict):
        raise BundleValidationError(f"{source_name}: bundle root must be an object")

    for field in ("id", "title", "kind", "passage", "rounds"):
        if field not in bundle:
            raise BundleValidationError(f"{source_name}: missing required field '{field}'")

    _require_non_empty_string(bundle["id"], f"{source_name}.id")
    _require_non_empty_string(bundle["title"], f"{source_name}.title")
    _require_non_empty_string(bundle["passage"], f"{source_name}.passage")

    kind = bundle["kind"]
    if kind not in ALLOWED_BUNDLE_KINDS:
        raise BundleValidationError(
            f"{source_name}.kind must be one of {sorted(ALLOWED_BUNDLE_KINDS)}; got {kind!r}"
        )

    grading = bundle.get("grading")
    if grading is not None and grading not in ALLOWED_GRADING_MODES:
        raise BundleValidationError(
            f"{source_name}.grading must be one of {sorted(ALLOWED_GRADING_MODES)}; got {grading!r}"
        )

    opt_desc = bundle.get("description")
    if opt_desc is not None and not isinstance(opt_desc, str):
        raise BundleValidationError(f"{source_name}.description must be a string or omitted")

    opt_ver = bundle.get("version")
    if opt_ver is not None and not isinstance(opt_ver, (str, int, float)):
        raise BundleValidationError(f"{source_name}.version must be a string/number or omitted")

    meta = bundle.get("metadata")
    if meta is not None and not isinstance(meta, dict):
        raise BundleValidationError(f"{source_name}.metadata must be an object or omitted")

    rounds = bundle["rounds"]
    if not isinstance(rounds, list) or len(rounds) == 0:
        raise BundleValidationError(f"{source_name}.rounds must be a non-empty array")

    for i, round_item in enumerate(rounds):
        prefix = f"{source_name}.rounds[{i}]"
        if not isinstance(round_item, dict):
            raise BundleValidationError(f"{prefix} must be an object")

        for field in ("id", "title", "prompt"):
            if field not in round_item:
                raise BundleValidationError(f"{prefix}: missing required field '{field}'")

        _require_non_empty_string(round_item["id"], f"{prefix}.id")
        _require_non_empty_string(round_item["title"], f"{prefix}.title")
        _require_non_empty_string(round_item["prompt"], f"{prefix}.prompt")

        round_kind = round_item.get("kind")
        if round_kind is not None and round_kind not in ALLOWED_ROUND_KINDS:
            raise BundleValidationError(
                f"{prefix}.kind must be one of {sorted(ALLOWED_ROUND_KINDS)}; got {round_kind!r}"
            )

        round_grading = round_item.get("grading")
        if round_grading is not None and round_grading not in ALLOWED_GRADING_MODES:
            raise BundleValidationError(
                f"{prefix}.grading must be one of {sorted(ALLOWED_GRADING_MODES)}; got {round_grading!r}"
            )

        acc_flag = round_item.get("accept_substrings")
        if acc_flag is not None:
            if not isinstance(acc_flag, bool):
                raise BundleValidationError(
                    f"{prefix}.accept_substrings must be a boolean (use 'substring_hints' for phrase lists); "
                    f"got {type(acc_flag).__name__}"
                )

        hints = round_item.get("substring_hints")
        if hints is not None:
            if not isinstance(hints, list) or not hints:
                raise BundleValidationError(
                    f"{prefix}.substring_hints must be a non-empty array of strings when present"
                )
            if not all(isinstance(h, str) and h.strip() for h in hints):
                raise BundleValidationError(
                    f"{prefix}.substring_hints must contain only non-empty strings"
                )

        keywords = round_item.get("keywords")
        if keywords is not None:
            if not isinstance(keywords, list) or not keywords or not all(
                isinstance(k, str) and k.strip() for k in keywords
            ):
                raise BundleValidationError(
                    f"{prefix}.keywords must be a non-empty array of non-empty strings when present"
                )

        mk = round_item.get("min_keyword_hits")
        if mk is not None:
            if not isinstance(mk, int) or mk < 1:
                raise BundleValidationError(
                    f"{prefix}.min_keyword_hits must be a positive integer when present"
                )

        rub = round_item.get("rubric")
        if rub is not None:
            if not isinstance(rub, str) or not rub.strip():
                raise BundleValidationError(f"{prefix}.rubric must be a non-empty string when present")

        ans = round_item.get("answer")
        if ans is not None and (not isinstance(ans, str) or not ans.strip()):
            raise BundleValidationError(f"{prefix}.answer must be a non-empty string when present")

        answers = round_item.get("answers")
        if answers is not None:
            if not isinstance(answers, list) or not answers:
                raise BundleValidationError(
                    f"{prefix}.answers must be a non-empty array of strings when present"
                )
            if not all(isinstance(a, str) and a.strip() for a in answers):
                raise BundleValidationError(f"{prefix}.answers entries must be non-empty strings")

        for fb_key in ("feedback_correct", "feedback_incorrect"):
            fb = round_item.get(fb_key)
            if fb is not None and not isinstance(fb, str):
                raise BundleValidationError(f"{prefix}.{fb_key} must be a string or omitted")

        if not _round_has_grading_input(round_item):
            raise BundleValidationError(
                f"{prefix}: must include at least one of rubric, keywords, answer, or answers (non-empty)"
            )

    return bundle
