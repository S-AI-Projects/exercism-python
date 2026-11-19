from functools import reduce

combine = lambda digits: reduce(lambda total, digit: total * 16 + digit, digits, 0)
print(combine([1, 10, 15]))
print(combine([]))
try:
    reduce(lambda total, digit: total * 16 + digit, [])
except TypeError:
    print("TypeError without initializer")
