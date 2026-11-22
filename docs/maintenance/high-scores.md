# HighScores Reference Implementation Scaling & Complexity Analysis

**Task Reference:** R36-T025  
**Exercise:** `exercises/practice/high-scores`  
**Target Class:** `HighScores` in `.meta/example.py`  

---

## 1. Input Domain & Sizing Definition

In terms of this exercise, the input size $n$ represents the number of recorded game scores ($n = \text{len}(\text{scores})$) passed to the `HighScores` constructor.

The exercise operates on a **variable-size input domain** consisting of non-empty lists of positive integer scores. Valid canonical test cases from `high_scores_test.py` span:
- **Size 1 ($n = 1$):** Single score boundary case (`[40]`, from `test_personal_top_when_there_is_only_one`).
- **Size 4 ($n = 4$):** Standard arcade session history (`[30, 50, 20, 70]`, from `test_list_of_scores` and `test_scores_after_personal_top_scores`).
- **Size 13 ($n = 13$):** Maximum canonical list size in the test suite (`[10, 30, 90, 30, 100, 20, 10, 0, 30, 40, 40, 70, 70]`, from `test_personal_top_three_from_a_list_of_scores`).

No arbitrary or synthetic benchmark sizes (e.g., $10^6$) are used; benchmarks strictly evaluate valid canonical inputs from the exercise domain.

---

## 2. Algorithmic Complexity

| Method | Time Complexity | Auxiliary Space | Operation Count / Nature of Work |
| :--- | :--- | :--- | :--- |
| `__init__(scores)` | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | Single pointer/reference assignment to `self.scores`. |
| `latest()` | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | Direct list index access (`self.scores[-1]`). |
| `personal_best()` | $\mathcal{O}(n)$ | $\mathcal{O}(1)$ | Linear scan evaluating $n - 1$ integer comparisons via built-in `max()`. |
| `personal_top_three()` | $\mathcal{O}(n \log n)$ | $\mathcal{O}(n)$ | Timsort via `sorted(self.scores, reverse=True)` ($\approx n \log_2 n$ comparisons) followed by a length-$\min(n, 3)$ slice. |

---

## 3. Empirical Benchmarking Methodology

- **Repetitions:** 15 repetitions per input size, holding input and environment constant.
- **Metric:** Median execution time in nanoseconds ($\text{ns}$) using high-resolution monotonic timer `time.perf_counter_ns()`.
- **Pre-assertion:** Correctness of outputs across all methods is asserted prior to timing.
- **Separation of Concerns:** In-process algorithmic execution is measured separately from Python process initialization overhead.

---

## 4. Benchmark Results

### A. Algorithm Execution Timings (In-Process)

| Input Size | Method | Median Time (ns) | Median Time (µs) | Operation Bound |
| :--- | :--- | :--- | :--- | :--- |
| **$n = 1$** | `__init__` | 125 ns | 0.12 µs | $\mathcal{O}(1)$ reference assignment |
| | `latest` | 83 ns | 0.08 µs | 1 index access |
| | `personal_best` | 84 ns | 0.08 µs | 0 comparisons ($n=1$) |
| | `personal_top_three` | 166 ns | 0.17 µs | Sort 1 item + slice |
| | **Full Lifecycle** | 333 ns | 0.33 µs | Combined operations |
| **$n = 4$** | `__init__` | 125 ns | 0.12 µs | $\mathcal{O}(1)$ reference assignment |
| | `latest` | 83 ns | 0.08 µs | 1 index access |
| | `personal_best` | 125 ns | 0.12 µs | 3 comparisons |
| | `personal_top_three` | 208 ns | 0.21 µs | Sort 4 items + slice 3 |
| | **Full Lifecycle** | 333 ns | 0.33 µs | Combined operations |
| **$n = 13$** | `__init__` | 84 ns | 0.08 µs | $\mathcal{O}(1)$ reference assignment |
| | `latest` | 83 ns | 0.08 µs | 1 index access |
| | `personal_best` | 166 ns | 0.17 µs | 12 comparisons |
| | `personal_top_three` | 250 ns | 0.25 µs | Sort 13 items + slice 3 |
| | **Full Lifecycle** | 417 ns | 0.42 µs | Combined operations |

### B. Algorithm Work vs. Process Startup Overhead

| Component | Measured Median Latency | Scale Comparison |
| :--- | :--- | :--- |
| Python Subprocess Startup (`python3 -c "pass"`) | ~12,042,667 ns (~12.04 ms) | $1.0\times$ (Baseline Overhead) |
| In-Process Full Lifecycle ($n = 13$) | 417 ns (~0.00042 ms) | **~28,800× faster** than process startup |
| `latest()` Operation ($n = 13$) | 83 ns (~0.00008 ms) | **~145,000× faster** than process startup |

This explicitly distinguishes algorithmic compute time from runtime invocation and compilation latency.

---

## 5. Limits of the Conclusion

1. **Domain Boundary:**
   The observed sub-microsecond performance holds within the canonical domain of arcade game sessions ($n \le 13$). Within this scale, constant factors dominate, and Python's optimized C implementation of Timsort (`sorted()`) outperforms overhead-heavy alternatives.
2. **Alternative for Large $n$:**
   If the domain were extended to large score streams ($n \gg 10^5$), `personal_top_three()` using full Timsort ($\mathcal{O}(n \log n)$ time and $\mathcal{O}(n)$ auxiliary memory) could be replaced by a bounded min-heap (`heapq.nlargest(3, ...)`), which scales in $\mathcal{O}(n \log 3) = \mathcal{O}(n)$ time and $\mathcal{O}(1)$ auxiliary space. However, for the defined exercise domain, `sorted(...)[:3]` remains idiomatic, readable, and highly optimal.
