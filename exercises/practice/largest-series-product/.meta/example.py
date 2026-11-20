from functools import reduce
from operator import mul


def slices(series, size):
    # Invariant: contiguous sub-sequences of length `size` with 0 <= size <= len(series).
    if size < 0:
        raise ValueError('span must not be negative')
    if size > len(series):
        raise ValueError('span must not exceed string length')
    if not all(item.isdigit() for item in series):
        raise ValueError('digits input must only contain digits')

    numbers = [int(digit) for digit in series]
    slice_count = len(numbers) - size + 1
    return [numbers[idx:idx + size] for idx in range(slice_count)]


def largest_product(series, size):
    if size == 0:
        return 1
    return max(reduce(mul, window) for window in slices(series, size))
