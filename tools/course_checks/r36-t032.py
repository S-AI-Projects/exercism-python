#!/usr/bin/env python3
"""
tools/course_checks/r36-t032.py
Focused regeneration and consistency check for ETL exercise.
"""

import os
import subprocess
import sys


def run_etl_regeneration_check():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    gen_script = os.path.join(repo_root, "bin", "generate_tests.py")
    spec_dir = os.path.join(repo_root, ".problem-specifications")

    assert os.path.exists(gen_script), f"Missing generate_tests.py at {gen_script}"
    assert os.path.exists(spec_dir), f"Missing .problem-specifications directory at {spec_dir}"

    env = os.environ.copy()
    venv_bin = os.path.join(repo_root, ".venv", "bin")
    if os.path.exists(venv_bin):
        env["PATH"] = f"{venv_bin}:{env.get('PATH', '')}"

    # Run generator check mode
    cmd = [sys.executable, gen_script, "--check", "-p", spec_dir, "etl"]
    proc = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        print(f"Generator stdout: {proc.stdout}")
        print(f"Generator stderr: {proc.stderr}", file=sys.stderr)
        raise RuntimeError(f"ETL test generator check failed with code {proc.returncode}")

    print("ETL test regeneration check passed: generated tests match repository tests byte-for-byte.")
    return True


if __name__ == "__main__":
    run_etl_regeneration_check()
