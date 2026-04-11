"""
Project: Homeschool Lessons (Dream.OS)
File: main.py
Purpose: Root entrypoint — delegates to run.py (`python main.py` from this folder).

Debugging 500 errors:
- Unhandled exceptions are logged to instance/homeschool-server.log (search for ERROR or Traceback).
- Global handler lives in app/__init__.py (not here — this file has no Flask app object).
- For interactive tracebacks in the browser (this PC only): set env HOMESCHOOL_DEV_SERVER=1 then python main.py
  (uses Flask dev server instead of Waitress; unset when done).
"""

from __future__ import annotations

import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "run.py"), run_name="__main__")
