"""Project launcher for running the MathMentor API or Discord bot from repo root."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent


def _run_python_file(relative_path: str) -> int:
    """Run a Python file in a child process and return its exit code."""
    target = REPO_ROOT / relative_path
    result = subprocess.run([sys.executable, str(target)], check=False)
    return result.returncode


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the root launcher."""
    parser = argparse.ArgumentParser(
        prog="python ai_tutor_launcher.py",
        description="MathMentor launcher: run API, Discord bot, or local checks.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("api", help="Run the Flask API server.")
    subparsers.add_parser("bot", help="Run the Discord bot.")
    subparsers.add_parser("test", help="Run API unit tests (mocked).")

    return parser


def main() -> int:
    """CLI entry point."""
    args = build_parser().parse_args()

    if args.command == "api":
        return _run_python_file("ai_tutor/api.py")
    if args.command == "bot":
        return _run_python_file("ai_tutor/bot.py")
    if args.command == "test":
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_ai_tutor_api.py", "-q"],
            cwd=REPO_ROOT,
            check=False,
        )
        return result.returncode

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
