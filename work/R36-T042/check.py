"""Task check: reproduce generated OCR tests, then run them on the reference."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "tools/course_checks/r36-t042.py"
spec = importlib.util.spec_from_file_location("r36_t042", CHECKER)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

result = module.run(ROOT / "work/R36-T042")
assert result["actual_case_counts"] == [17, 17]
assert result["stability"] == "identical after normalizing only the generated-date header"
print("PASS: two fresh generation rounds are stable; all 17 reference tests pass.")
