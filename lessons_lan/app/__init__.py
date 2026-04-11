"""
Project: Homeschool Lessons (Dream.OS)
File: app/__init__.py
Purpose: Flask application factory and app wiring (db, plugins, routes).
Owner: Local family deployment (homeschool)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Repo root must be importable (vocabulary_game, spelling_lab_core) no matter how Flask is started.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from flask import Flask
from werkzeug.exceptions import HTTPException

from .db import init_app as init_db
from .logging_setup import attach_logging, install_wsgi_boundary_logger, register_request_logging
from .plugin_loader import load_plugins


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev-change-me",
    )

    # MCQ templates expect JSON arrays; bad DB rows must not 500 the page.
    import json as _json

    def _safe_fromjson(value):
        try:
            return _json.loads(value or "[]")
        except (_json.JSONDecodeError, TypeError, ValueError):
            return []

    app.jinja_env.filters["fromjson"] = _safe_fromjson

    init_db(app)
    load_plugins(app)

    from .routes import bp as routes_bp
    from .spelling_lab_routes import bp as spelling_lab_bp
    from .vocab_signal_routes import bp as vocab_signal_bp

    app.register_blueprint(routes_bp)
    app.register_blueprint(spelling_lab_bp)
    app.register_blueprint(vocab_signal_bp)

    attach_logging(app)
    register_request_logging(app)
    install_wsgi_boundary_logger(app)

    @app.errorhandler(Exception)
    def _log_unhandled(exc: BaseException):
        """Log full trace to file + stderr; safe response for the browser."""
        if isinstance(exc, HTTPException):
            return exc
        app.logger.exception("Unhandled exception (500): %s", exc)
        return (
            "<h1>Internal Server Error</h1>"
            "<p>Details were written to the server log file next to your database "
            "(usually <code>instance/homeschool-server.log</code>) and the terminal.</p>",
            500,
        )

    return app

