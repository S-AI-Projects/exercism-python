# Each candidate and the target are lowercased and sorted per comparison; for
# k similarly sized words of length m this costs O(k * m log m).
def find_anagrams(word, candidates):
    return [candidate
            for candidate in candidates
            if _letters(candidate) == _letters(word)
            if candidate.lower() != word.lower()]


def _letters(word):
    return sorted(word.lower())
