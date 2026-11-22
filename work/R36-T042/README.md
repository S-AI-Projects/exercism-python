# R36-T042 evidence

Run `python3 work/R36-T042/check.py` from the repository root with Python 3.13,
pytest, and the generator dependencies from `requirements-generator.txt` available.
The check builds two clean temporary generator trees, includes the exercise's
dotfiles, substitutes `.meta/example.py` only in each temporary learner file,
regenerates tests with the repository's `bin/generate_tests.py`, and runs pytest.
It rejects generation/test failures, missing anchor cases, zero or unexpected
case counts, and any difference other than the generated-date header.

The canonical input is a committed snapshot from
`exercism/problem-specifications` at
`4812c213a2647e2034ad5ac78155ce9265cdd171`:
`inputs/ocr-numbers-canonical-data.json`. The repository template and generator
remain the code under test. Generated artifacts are written only to temporary
directories; `results.json` records the expected and actual case counts,
commands' output, and tool versions.
