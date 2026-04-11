"""
Project: Homeschool Lessons (Dream.OS)
File: run.py
Purpose: Production entrypoint to serve the web app on the LAN.
Owner: Local family deployment (homeschool)
"""

from __future__ import annotations

import logging
import socket
import sys
import threading
import time
from pathlib import Path

# Ensure project root is on sys.path (imports: app, vocabulary_game, spelling_lab_core).
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app import create_app

app = create_app()


def _lan_ipv4_hints() -> list[str]:
    """IPv4 addresses other LAN devices should use (not 127.0.0.1)."""
    out: set[str] = set()
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            probe.settimeout(0.25)
            probe.connect(("8.8.8.8", 80))
            ip = probe.getsockname()[0]
            if ip and not ip.startswith("127."):
                out.add(ip)
        finally:
            probe.close()
    except OSError:
        pass
    try:
        for fam, *_rest, sockaddr in socket.getaddrinfo(socket.gethostname(), None):
            if fam != socket.AF_INET:
                continue
            ip = sockaddr[0]
            if ip and not ip.startswith("127."):
                out.add(ip)
    except OSError:
        pass
    return sorted(out)


def _heartbeat_stdout(interval_sec: float = 120.0, first_after_sec: float = 25.0) -> None:
    """Periodic line so you can tell the process is not frozen when nobody is clicking."""

    log = logging.getLogger("homeschool.heartbeat")

    def loop():
        time.sleep(first_after_sec)
        while True:
            log.info(
                "Server tick - still alive, waiting for HTTP requests. (Ctrl+C to stop.)",
            )
            time.sleep(interval_sec)

    threading.Thread(target=loop, daemon=True, name="homeschool-heartbeat").start()


if __name__ == "__main__":
    # create_app() already configured file + stderr logging (see app/logging_setup.py).
    import os

    boot = logging.getLogger("homeschool.boot")

    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "5000"))
    dev = os.environ.get("HOMESCHOOL_DEV_SERVER", "").strip().lower() in ("1", "true", "yes")
    hints = _lan_ipv4_hints()
    if hints:
        lan_lines = "\n".join(
            f"  Same Wi‑Fi:  http://{h}:{port}/login  →  then open Games → Spelling Lab"
            for h in hints
        )
    else:
        lan_lines = (
            "  Same Wi‑Fi:  http://<THIS-PC-IP>:5000/login  (run ipconfig to find IP; not 127.0.0.1)"
        )

    banner = (
        f"\n{'=' * 60}\n"
        f"Homeschool Lessons — {'Flask DEV (debug)' if dev else 'Waitress'}\n"
        f"{'=' * 60}\n"
        f"  Log file: instance/homeschool-server.log (and stderr below)\n"
        f"  Set HOMESCHOOL_LOG_LEVEL=DEBUG for verbose request logs.\n"
        f"  This PC:  http://127.0.0.1:{port}/login\n"
        f"  Spelling Lab:  http://127.0.0.1:{port}/spelling-lab\n"
        f"  Vocabulary Breaker:  http://127.0.0.1:{port}/games/vocabulary-signal-breaker\n"
        f"{lan_lines}\n\n"
        f"  If other devices cannot connect: Windows Firewall -> allow port {port} for private networks,\n"
        f"  or allow Python/Waitress when prompted.\n\n"
        f"Below: each HTTP request logs with timing; unhandled errors include full tracebacks.\n"
        f"{'=' * 60}\n"
    )
    print(banner, flush=True)

    if dev:
        print(
            "\n*** HOMESCHOOL_DEV_SERVER is on: using Flask's built-in server with DEBUG.\n"
            "*** Tracebacks may appear in the BROWSER — use only on this PC, not on the LAN.\n"
            "*** Unset HOMESCHOOL_DEV_SERVER or set to 0 to use Waitress again.\n",
            flush=True,
        )
        boot.info("Flask dev server host=%s port=%s debug=True", host, port)
        _heartbeat_stdout()
        # use_reloader=False: avoids double create_app() and duplicate log handlers
        app.run(host=host, port=port, debug=True, use_reloader=False, threaded=True)
    else:
        from waitress import serve

        boot.info("Waitress starting host=%s port=%s", host, port)
        _heartbeat_stdout()
        serve(app, host=host, port=port)
