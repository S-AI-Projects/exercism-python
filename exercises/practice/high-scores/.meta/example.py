class HighScores:
    """
    Manages a player's score history and provides summary metrics.

    Algorithmic Complexity & Operational Invariants:
    Let n = len(scores) be the number of score records in the player's history.
    - __init__(scores):
        Time: O(1).
        Space: O(1) auxiliary (stores a reference to the scores list).
        Invariant: scores is a non-empty list of positive integers representing game scores.
    - latest():
        Time: O(1).
        Space: O(1) auxiliary.
        Invariant: Accesses the most recently recorded score at self.scores[-1] in constant time.
    - personal_best():
        Time: O(n).
        Space: O(1) auxiliary.
        Invariant: Performs a single linear scan evaluating n - 1 comparisons via max().
    - personal_top_three():
        Time: O(n log n).
        Space: O(n) auxiliary.
        Invariant: Utilizes Timsort (sorted()) to order elements descending and slices
        at most min(n, 3) items without mutating the underlying self.scores attribute.
    """

    def __init__(self, scores):
        self.scores = scores

    def latest(self):
        return self.scores[-1]

    def personal_best(self):
        return max(self.scores)

    def personal_top_three(self):
        return sorted(self.scores, reverse=True)[:3]
