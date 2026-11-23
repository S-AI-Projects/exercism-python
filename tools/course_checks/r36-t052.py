#!/usr/bin/env python3
"""
Reusable focused regeneration check for resistor-color (R36-T052).
Verifies that test generation is reproducible across isolated runs
with only timestamp differences permitted.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile


def normalize_content(content: str) -> str:
    # Normalize timestamp line '# File last updated on YYYY-MM-DD'
    return re.sub(r"# File last updated on \d{4}-\d{2}-\d{2}", "# File last updated on <TIMESTAMP>", content)


def check_regeneration(repo_root: str = None) -> bool:
    if repo_root is None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    test_file_rel = os.path.join("exercises", "practice", "resistor-color", "resistor_color_test.py")
    orig_test_path = os.path.join(repo_root, test_file_rel)

    with open(orig_test_path, "r", encoding="utf-8") as f:
        orig_content = f.read()

    with tempfile.TemporaryDirectory() as tmp_root:
        copy1 = os.path.join(tmp_root, "copy1")
        copy2 = os.path.join(tmp_root, "copy2")

        # Copy essential repository structure to both scratch environments
        for copy_dir in [copy1, copy2]:
            os.makedirs(os.path.join(copy_dir, "exercises", "practice"), exist_ok=True)
            shutil.copytree(os.path.join(repo_root, "exercises", "practice", "resistor-color"),
                            os.path.join(copy_dir, "exercises", "practice", "resistor-color"))
            shutil.copytree(os.path.join(repo_root, "config"), os.path.join(copy_dir, "config"))
            shutil.copytree(os.path.join(repo_root, "bin"), os.path.join(copy_dir, "bin"))
            if os.path.exists(os.path.join(repo_root, ".problem-specifications")):
                shutil.copytree(os.path.join(repo_root, ".problem-specifications"),
                                os.path.join(copy_dir, ".problem-specifications"))

            # Execute generation
            cmd = [sys.executable, os.path.join(copy_dir, "bin", "generate_tests.py"), "resistor-color"]
            res = subprocess.run(cmd, cwd=copy_dir, capture_output=True, text=True)
            if res.returncode != 0:
                print(f"Generation failed in {copy_dir}:\n{res.stderr}", file=sys.stderr)
                return False

        # Read generated test files from both runs
        gen1_file = os.path.join(copy1, test_file_rel)
        gen2_file = os.path.join(copy2, test_file_rel)

        with open(gen1_file, "r", encoding="utf-8") as f:
            c1 = f.read()
        with open(gen2_file, "r", encoding="utf-8") as f:
            c2 = f.read()

        # Check normalization
        n1 = normalize_content(c1)
        n2 = normalize_content(c2)

        if n1 != n2:
            print("Error: Successive test generations yielded differing outputs!", file=sys.stderr)
            return False

        # Ensure no cases silently dropped
        anchor_cases = ["test_black", "test_white", "test_orange", "test_colors"]
        for case in anchor_cases:
            if f"def {case}" not in n1:
                print(f"Error: Anchor case {case} missing from generated tests!", file=sys.stderr)
                return False

        print("Regeneration check verified: Two isolated generations produce identical normalized suites.")
        return True


if __name__ == "__main__":
    success = check_regeneration()
    sys.exit(0 if success else 1)
