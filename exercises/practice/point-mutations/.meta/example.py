def hamming_distance(strand1, strand2):
    # Only aligned positions count; zip intentionally ignores trailing bases.
    mismatch_count = sum(base1 != base2 for base1, base2 in zip(strand1, strand2))
    return mismatch_count
