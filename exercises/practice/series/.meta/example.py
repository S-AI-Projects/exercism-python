def slices(series, length):
    if not series:
        raise ValueError('series cannot be empty')
    elif length == 0:
        raise ValueError('slice length cannot be zero')
    elif length < 0:
        raise ValueError('slice length cannot be negative')
    elif len(series) < length:
        raise ValueError('slice length cannot be greater than series length')

    # The last valid start is len(series) - length, so the range is exclusive.
    last_start = len(series) - length + 1
    return [series[start : start + length] for start in range(last_start)]
