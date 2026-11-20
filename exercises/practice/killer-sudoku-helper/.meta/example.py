import itertools


# Complexity: For cage size `s` and candidates `n = len(possible)` <= 9,
# itertools.combinations examines C(n, k) tuples as k decreases from n to 1.
# Since n <= 9, the total search space is strictly bounded by sum_{k=1}^n C(n, k) <= 2^9 - 1 = 511
# candidate combinations, yielding O(2^|D|) bounded algorithm work and O(|D|) space for fixed Sudoku cages.
def combinations(target, size, exclude):
    result = []
    possible = [index for index in
                range(1, int((target ** 2 /size) ** 0.6))
                if index not in exclude]

    if size == 1:
        return [[target]]
    else:
        for index in range(len(possible), 0, -1):
            for seq in itertools.combinations(possible, index):
                if sum(seq) == target and len(seq) == size:
                    result.append(list(seq))
    return result
