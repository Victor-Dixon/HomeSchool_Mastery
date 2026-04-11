"""
Centralized logging: rotating file under Flask instance/, console, request timing.
Env: HOMESCHOOL_LOG_LEVEL=DEBUG|INFO|WARNING (default INFO)
"""

from __future__ import annotations

import logging
import logging.handlers
import os
import sys
import time
import uuid
from pathlib import Path

from flask import Flask

_CONFIGURED = False


def _level_from_env() -> int:
    name = (os.environ.get("HOMESCHOOL_LOG_LEVEL") or "INFO").strip().upper()
    return getattr(logging, name, logging.INFO)


def attach_logging(app: Flask) -> Path | None:
    """
    Attach rotating file + stderr handlers to the root logger (once).
    Returns the log file path, or None if skipped.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return getattr(attach_logging, "_log_path", None)

    os.makedirs(app.instance_path, exist_ok=True)
    log_path = Path(app.instance_path) / "homeschool-server.log"

    level = _level_from_env()
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    fh = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    fh.setLevel(level)
    fh.setFormatter(fmt)

    sh = logging.StreamHandler(sys.stderr)
    sh.setLevel(level)
    sh.setFormatter(fmt)

    root.addHandler(fh)
    root.addHandler(sh)

    logging.getLogger("waitress").setLevel(logging.INFO)
    logging.getLogger("waitress.queue").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info(
        "Logging initialized file=%s level=%s (HOMESCHOOL_LOG_LEVEL=DEBUG for verbose requests)",
        log_path,
        logging.getLevelName(level),
    )

    _CONFIGURED = True
    attach_logging._log_path = log_path  # type: ignore[attr-defined]
    return log_path


def register_request_logging(app: Flask) -> None:
    """Log each request with id, method, path, status, duration (ms)."""

    @app.before_request
    def _req_begin():
        from flask import g, request

        g._log_req_id = uuid.uuid4().hex[:10]
        g._log_t0 = time.perf_counter()
        try:
            # Avoid logging bodies (passwords); query string only at DEBUG
            if app.debug or app.logger.isEnabledFor(logging.DEBUG):
                qs = (request.query_string or b"").decode("utf-8", "replace")
                qpart = f"?{qs}" if qs else ""
                app.logger.debug(
                    "req %s %s %s%s",
                    g._log_req_id,
                    request.method,
                    request.path,
                    qpart,
                )
        except Exception:
            logging.getLogger("homeschool.logging").exception("before_request log failed")

    @app.after_request
    def _req_end(response):
        from flask import g, request

        try:
            rid = getattr(g, "_log_req_id", "--------")
            t0 = getattr(g, "_log_t0", None)
            ms = (time.perf_counter() - t0) * 1000 if t0 is not None else -1.0
            app.logger.info(
                "req %s %s %s -> %s %.1fms",
                rid,
                request.method,
                request.path,
                response.status_code,
                ms,
            )
        except Exception:
            # Never let a logging/IO failure (e.g. locked log file) become HTTP 500.
            logging.getLogger("homeschool.logging").exception("after_request log failed")
        return response


def install_wsgi_boundary_logger(app: Flask) -> None:
    """Last-resort traceback if something escapes Flask's normal error handling."""

    inner = app.wsgi_app
    log = logging.getLogger("homeschool.wsgi")

    def wsgi_app(environ, start_response):
        try:
            return inner(environ, start_response)
        except BaseException:
            log.exception(
                "Uncaught exception at WSGI boundary (path=%s)",
                environ.get("PATH_INFO", "?"),
            )
            raise

    app.wsgi_app = wsgi_app

