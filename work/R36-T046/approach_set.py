"""Independent, cached-set representation for the allergies contract."""


class Allergies:
    _allergies = [
        "eggs",
        "peanuts",
        "shellfish",
        "strawberries",
        "tomatoes",
        "chocolate",
        "pollen",
        "cats",
    ]

    def __init__(self, score):
        self.score = score

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        self._selected = frozenset(
            item
            for bit, item in enumerate(self._allergies)
            if value & (1 << bit)
        )

    def allergic_to(self, item):
        # Preserve the reference behavior for names outside the known list.
        self._allergies.index(item)
        return item in self._selected

    @property
    def lst(self):
        return [item for item in self._allergies if item in self._selected]
