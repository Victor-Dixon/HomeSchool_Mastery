"""
Tests for Story Duel and /games hub.
"""

import json

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "story_duel_test.db"
    a = create_app()
    a.config.update(
        TESTING=True,
        SECRET_KEY="test-story-duel",
        DATABASE=str(db_path),
        STORY_DUEL_BUNDLE_ID="marcus_wallet_v1",
    )
    with a.app_context():
        from app.db import init_db, seed_if_empty

        init_db()
        seed_if_empty()
    yield a


def login(client, username, password):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)


@pytest.fixture(autouse=True)
def _story_duel_disable_ollama_for_deterministic_tests(monkeypatch):
    """CI has no Ollama; heuristic grading must still pass integration tests."""
    import app.story_duel as sd

    monkeypatch.setattr(sd, "ollama_grade_short_answer", lambda **kw: (None, ""))


def test_games_hub_loads(app):
    c = app.test_client()
    login(c, "charlie", "34086028")
    r = c.get("/games")
    assert r.status_code == 200
    assert b"Story Duel" in r.data
    assert b"/demo/story-duel" in r.data
    assert b"Games" in r.data or b"Today" in r.data


def test_play_alias_redirects_to_games_hub(app):
    c = app.test_client()
    login(c, "charlie", "34086028")
    r = c.get("/play", follow_redirects=False)
    assert r.status_code == 302
    assert "/games" in (r.headers.get("Location") or "")


def test_story_duel_demo_start_and_round(app):
    c = app.test_client()
    login(c, "charlie", "34086028")
    r = c.post("/api/story-duel/demo/start")
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("ok") is True
    assert "bundle" in data
    assert "Marcus" in data["bundle"]["passage"]

    token = data["duel_token"]
    assert isinstance(token, str) and len(token) > 8
    r2 = c.post(
        "/api/story-duel/demo/round",
        data=json.dumps(
            {
                "answer": "Marcus finds a wallet and walks to the office to return it.",
                "ms_elapsed": 2000,
                "duel_token": token,
            }
        ),
        content_type="application/json",
    )
    assert r2.status_code == 200
    d2 = r2.get_json()
    assert d2.get("ok") is True
    assert d2.get("correct") is True
    assert d2.get("ai_hp") < 100
    assert d2.get("duel_token")


def test_story_duel_advances_round_with_signed_token(app):
    """Regression: round index must advance so prompts change (no flaky session cookie)."""
    c = app.test_client()
    login(c, "charlie", "34086028")
    r = c.post("/api/story-duel/demo/start")
    d0 = r.get_json()
    tok = d0["duel_token"]
    r1 = c.post(
        "/api/story-duel/demo/round",
        json={
            "answer": "Marcus finds a wallet and walks to the office to return it.",
            "ms_elapsed": 2000,
            "duel_token": tok,
        },
    )
    d1 = r1.get_json()
    assert d1.get("next_round", {}).get("id") == "inference"
    tok2 = d1["duel_token"]
    r2 = c.post(
        "/api/story-duel/demo/round",
        json={
            "answer": "He will return the wallet to the office because he is honest.",
            "ms_elapsed": 2000,
            "duel_token": tok2,
        },
    )
    d2 = r2.get_json()
    assert d2.get("next_round", {}).get("id") == "theme"


def test_wrong_lesson_redirects_to_games_hub(app):
    c = app.test_client()
    login(c, "charlie", "34086028")
    r = c.get("/lesson/9999", follow_redirects=False)
    assert r.status_code == 302
    assert "/games" in (r.headers.get("Location") or "")


def test_bundle_id_from_lesson_notes():
    from app.story_duel_loader import bundle_id_from_lesson_notes

    assert bundle_id_from_lesson_notes("Intro\nstory_duel_bundle:storm_library_v1\n") == "storm_library_v1"
    assert bundle_id_from_lesson_notes(None) is None


def test_load_story_bundles():
    from app.story_duel_loader import load_story_bundle

    m = load_story_bundle("marcus_wallet_v1")
    assert m["id"] == "marcus_wallet_v1"
    assert "Marcus" in m["passage"]
    storm = load_story_bundle("storm_library_v1")
    assert "Maya" in storm["passage"]
    vocab = load_story_bundle("vocab_ocean_v1")
    assert vocab["rounds"][0].get("kind") == "vocabulary_define"


def test_grade_round_uses_ollama_when_it_returns_verdict(monkeypatch):
    import app.story_duel as sd

    monkeypatch.setattr(sd, "ollama_grade_short_answer", lambda **kw: (True, "Strong use of evidence."))
    ok, src, fb = sd.grade_round_answer(
        answer="complete nonsense that would fail keywords",
        spec={
            "title": "Q",
            "prompt": "What happens?",
            "rubric": "Anything goes for this test.",
            "substring_hints": ["zzzzzz"],
            "keywords": ["zzzzzz"],
            "min_keyword_hits": 9,
        },
        passage="Tiny passage.",
        bundle={"grading": "auto"},
    )
    assert ok is True
    assert src == "ollama"
    assert "evidence" in fb.lower()


def test_demo_round_returns_grading_fields(app):
    c = app.test_client()
    login(c, "charlie", "34086028")
    s = c.post("/api/story-duel/demo/start").get_json()
    r = c.post(
        "/api/story-duel/demo/round",
        data=json.dumps(
            {
                "answer": "Marcus finds a wallet and walks to the office to return it.",
                "ms_elapsed": 2000,
                "duel_token": s["duel_token"],
            }
        ),
        content_type="application/json",
    )
    d = r.get_json()
    assert d.get("grading_source") == "heuristic"


def test_validate_vocab_bundle_minimal():
    from app.story_duel_schema import validate_story_bundle

    validate_story_bundle(
        {
            "id": "vocab_test",
            "title": "Vocab Test",
            "kind": "vocabulary",
            "passage": "Word bank",
            "rounds": [
                {
                    "id": "r1",
                    "title": "Void",
                    "kind": "vocabulary_define",
                    "prompt": "Define void",
                    "keywords": ["empty"],
                }
            ],
        },
        source_name="vocab_test.json",
    )


def test_validate_bundle_rejects_empty_rounds():
    from app.story_duel_schema import BundleValidationError, validate_story_bundle

    with pytest.raises(BundleValidationError):
        validate_story_bundle(
            {
                "id": "bad",
                "title": "Bad",
                "kind": "vocabulary",
                "passage": "x",
                "rounds": [],
            },
            source_name="bad.json",
        )


def test_validate_bundle_rejects_round_without_grading_inputs():
    from app.story_duel_schema import BundleValidationError, validate_story_bundle

    with pytest.raises(BundleValidationError):
        validate_story_bundle(
            {
                "id": "bad2",
                "title": "Bad2",
                "kind": "vocabulary",
                "passage": "x",
                "rounds": [{"id": "r1", "title": "R1", "prompt": "Define void"}],
            },
            source_name="bad2.json",
        )


def test_validate_rejects_invalid_top_level_kind():
    from app.story_duel_schema import BundleValidationError, validate_story_bundle

    with pytest.raises(BundleValidationError) as exc:
        validate_story_bundle(
            {
                "id": "x",
                "title": "T",
                "kind": "novel",
                "passage": "p",
                "rounds": [{"id": "r1", "title": "Q", "prompt": "q", "keywords": ["a"]}],
            },
            source_name="x.json",
        )
    assert "kind" in str(exc.value).lower()


def test_validate_rejects_invalid_grading_mode():
    from app.story_duel_schema import BundleValidationError, validate_story_bundle

    with pytest.raises(BundleValidationError):
        validate_story_bundle(
            {
                "id": "x",
                "title": "T",
                "kind": "story_duel",
                "passage": "p",
                "grading": "magic",
                "rounds": [{"id": "r1", "title": "Q", "prompt": "q", "keywords": ["a"]}],
            },
            source_name="x.json",
        )


def test_validate_rejects_invalid_round_kind():
    from app.story_duel_schema import BundleValidationError, validate_story_bundle

    with pytest.raises(BundleValidationError):
        validate_story_bundle(
            {
                "id": "x",
                "title": "T",
                "kind": "story_duel",
                "passage": "p",
                "rounds": [{"id": "r1", "title": "Q", "kind": "dragon_fire", "prompt": "q", "keywords": ["a"]}],
            },
            source_name="x.json",
        )


def test_validate_rejects_missing_round_title():
    from app.story_duel_schema import BundleValidationError, validate_story_bundle

    with pytest.raises(BundleValidationError) as exc:
        validate_story_bundle(
            {
                "id": "x",
                "title": "T",
                "kind": "vocabulary",
                "passage": "p",
                "rounds": [{"id": "r1", "prompt": "q", "keywords": ["a"]}],
            },
            source_name="x.json",
        )
    assert "title" in str(exc.value).lower()


def test_validate_rejects_accept_substrings_as_list():
    from app.story_duel_schema import BundleValidationError, validate_story_bundle

    with pytest.raises(BundleValidationError) as exc:
        validate_story_bundle(
            {
                "id": "x",
                "title": "T",
                "kind": "vocabulary",
                "passage": "p",
                "rounds": [
                    {
                        "id": "r1",
                        "title": "Q",
                        "prompt": "q",
                        "accept_substrings": ["not", "a", "boolean"],
                        "keywords": ["a"],
                    }
                ],
            },
            source_name="x.json",
        )
    assert "boolean" in str(exc.value).lower()


def test_load_vocab_genesis_bundle():
    from app.story_duel_loader import load_story_bundle

    g = load_story_bundle("vocab_genesis_v1")
    assert g["kind"] == "vocabulary"
    assert g["id"] == "vocab_genesis_v1"
    assert len(g["rounds"]) >= 10
    assert any(r["id"] == "genesis_void_define" for r in g["rounds"])
    assert any(r["id"] == "genesis_genesis_define" for r in g["rounds"])
    assert any(r["id"] == "genesis_water_define" for r in g["rounds"])
