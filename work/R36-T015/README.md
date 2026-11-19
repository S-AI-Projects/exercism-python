# R36-T015 evidence

Run `python3 work/R36-T015/check.py` from the repository root. The check reads the exercise filenames from `.meta/config.json`, copies the complete exercise tree (including hidden metadata) into a temporary directory, substitutes `.meta/example.py` only for the solution file in that copy, and runs the configured tests there. It records expected and actual test counts, pytest output, and Python/pytest versions beside the check.

Input size is the number of deposit transactions in an account history. The check verifies histories of 1, 2, and 5 valid deposits before timing; it takes seven median samples per size, each sample processing 1,000 independent histories. Account construction/opening is outside the timed region. The report distinguishes those operation timings from pytest process startup and includes the interpreter/platform versions and expected versus actual balances.
