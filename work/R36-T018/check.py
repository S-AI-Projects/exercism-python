#!/usr/bin/env python3
"""Coursework entry point for the nth-prime metadata validation."""

from pathlib import Path
import runpy


CHECKER = Path(__file__).resolve().parents[2] / "tools/course_checks/r36-t018.py"
runpy.run_path(str(CHECKER), run_name="__main__")
