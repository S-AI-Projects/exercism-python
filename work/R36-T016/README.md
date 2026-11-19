# R36-T016 comparison evidence

The maintained reference evaluates the source digits as one Python integer using positional powers, then extracts target-base digits by repeated division and remainders. `alternative.py` instead streams source digits into a target-base digit vector, stored least-significant digit first, using multiply-and-carry updates.

The digit-vector representation can make the target-base invariant more visible and avoids constructing one whole-number intermediate. It adds carry logic, a list proportional to the output length, and repeated updates across that list for each source digit. The reference is shorter and benefits from Python's built-in arbitrary-precision arithmetic; its work still depends on the integer sizes involved. Neither approach is claimed faster.

Run `python3 work/R36-T016/check.py` at the repository root. It copies the exercise including dotfiles into separate temporary directories, substitutes the reference or `alternative.py` only into each temporary solution path, and invokes `python3 -m pytest -q` with the same enabled tests. It checks both child return codes and test counts, and records expected/actual results, output, and tool versions here.
