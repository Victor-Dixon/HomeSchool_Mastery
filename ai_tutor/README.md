# AI Tutor Support Package

> Updated: 2026-07-03

## What this package is

`ai_tutor/` is a support package inside HomeSchool_Mastery. It provides a Flask
API and Discord bot for Ollama-backed homework help and TEKS-style quiz support.

It is present in the repository but is not the canonical HomeSchool Mastery app.
The canonical app is `../lessons_lan/`.

## Why it exists

It offers optional tutoring support outside the canonical `lessons_lan/` SQLite
domain: free-form homework help, structured quiz explanations, Discord quiz
commands, and per-Discord-user JSON progress.

## Domain

Support domain: AI-assisted tutoring and Discord-based practice.

Canonical platform domain remains family homeschool education and learner
accountability in `lessons_lan/`.

## Main components

| File | Purpose |
|---|---|
| `api.py` | Flask API with `GET /health`, `POST /ask`, and `POST /explain` |
| `tutor.py` | Ollama prompt wrapper |
| `bot.py` | Discord bot entrypoint |
| `cogs/` | Discord command modules |
| `questions.py` | TEKS-style support question bank |
| `progress.py` | JSON progress tracking in `data/progress.json` |
| `.env.example` | Environment variable template |

## Run API

From the repository root:

```bash
pip install -r requirements.txt
python -m ai_tutor.api
```

The API uses `PORT` if set, otherwise port `5000`. Avoid running it on the same
port as `lessons_lan/`.

## Run Discord bot

```bash
pip install -r requirements.txt
python -m ai_tutor.bot
```

Requires a Discord token in environment configuration. See `.env.example`.

## Data

`ai_tutor/progress.py` writes per-user support progress to:

```text
data/progress.json
```

This is separate from `lessons_lan/instance/homeschool.db`.

## Current status

Completed:

- API endpoints exist and have root tests in `tests/test_ai_tutor_api.py`.
- Discord cogs and question/progress helpers are present.
- Ollama environment variables are documented in `.env.example`.

Remaining:

- Decide whether `ai_tutor/` stays a separate support package or integrates with
  `lessons_lan/`.
- If integrated, define shared data flow, persistence, routes, and tests.
