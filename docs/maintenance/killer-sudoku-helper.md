# Killer Sudoku Helper cost study

## Input model and scope

In Killer Sudoku, cages specify a `target` sum, a cage `size` ($1 \le \text{size} \le 9$), and an `exclude` list of already assigned digits. The universe of candidate digits is bounded by the non-excluded digits from $\{1, 2, \dots, 9\}$. Because standard Sudoku cages contain at most 9 distinct cells, the candidate pool size $n \le 9$ is strictly bounded.

The reference implementation in `.meta/example.py` uses `itertools.combinations(possible, index)` where `index` ranges from $n$ down to 1. For a fixed set of candidates, the maximum number of combinations evaluated across all iterations is at most $\sum_{k=1}^n \binom{n}{k} \le 2^9 - 1 = 511$.

## Input sizes and operation counts

We examine three representative valid cage sizes from the problem domain:

| Input case | Cage size | Target sum | Exclude | Candidate domain size | Combinations evaluated | Expected output |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| `size = 1` | 1 | 1 | `[]` | 1 | 0 (short-circuited) | `[[1]]` |
| `size = 3` | 3 | 7 | `[]` | 4 (`[1, 2, 3, 4]`) | $\sum_{k=1}^4 \binom{4}{k} = 15$ | `[[1, 2, 4]]` |
| `size = 9` | 9 | 45 | `[]` | 9 (`[1..9]`) | $\sum_{k=1}^9 \binom{9}{k} = 511$ | `[[1, 2, 3, 4, 5, 6, 7, 8, 9]]` |

## Measurements

`work/R36-T005/check.py` evaluates each input size across 7 repetitions (1,000 iterations per repetition) after verifying correctness and ensuring environment constants.

The algorithm work is strictly bounded by the fixed digit alphabet $\{1..9\}$ in Sudoku cages. Process startup, Python interpreter initialization, and pytest test runner overhead are separated from these core algorithmic operation counts.
