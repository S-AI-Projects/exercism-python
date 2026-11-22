# Food Chain file map

The runner uses the `files` object in
`exercises/practice/food-chain/.meta/config.json` to locate exercise files.
Paths are relative to the exercise directory:

| Role | Config path | Purpose |
| --- | --- | --- |
| `solution` | `food_chain.py` | Learner starter; intentionally left unsolved. |
| `test` | `food_chain_test.py` | Generated Python test module. |
| `example` | `.meta/example.py` | Maintained reference implementation used for isolated checks. |
| `editor` | Not declared | There is no separate editor file; the solution path is the learner-editable file. |

The test module is generated from canonical exercise data, `.meta/tests.toml`,
and `.meta/template.j2`; it is not a hand-maintained file. The runner reads the
`test` entry and imports `food_chain_test.py`, whose `from food_chain import
recite` import resolves to the exercise's solution filename. A maintenance
check copies the exercise including dotfiles, copies `.meta/example.py` to the
configured solution path in that temporary copy, and runs `python3 -m pytest
-q` there. The reusable metadata validator rejects parent traversal, paths
outside the exercise (including symlink escapes), and missing declared files.

Reproduce the validation, three negative fixtures, and all ten reference cases
from the repository root with:

```sh
python3 work/R36-T048/check.py
```
