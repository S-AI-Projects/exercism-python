def is_armstrong_number(number):
    # Invariant: An Armstrong number equals the sum of each digit raised to the total digit count.
    digits_str = str(number)
    num_digits = len(digits_str)
    return sum(int(digit) ** num_digits for digit in digits_str) == number
