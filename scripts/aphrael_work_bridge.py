"""Command-line entry point for Aphrael's native Work bridge tools."""

from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from plugins.aphrael_guardrails.work_bridge import *  # noqa: F401,F403,E402


if __name__ == "__main__":
    raise SystemExit(main())
