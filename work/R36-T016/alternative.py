"""Digit-vector alternative for the all-your-base exercise."""


def rebase(input_base, digits, output_base):
    if input_base < 2:
        raise ValueError("input base must be >= 2")
    if output_base < 2:
        raise ValueError("output base must be >= 2")
    if any(digit < 0 or digit >= input_base for digit in digits):
        raise ValueError("all digits must satisfy 0 <= d < input base")

    # Keep the accumulated value as output-base digits, least significant first.
    converted = [0]
    for source_digit in digits:
        carry = source_digit
        position = 0
        while position < len(converted):
            carry += converted[position] * input_base
            converted[position], carry = carry % output_base, carry // output_base
            position += 1
        while carry:
            converted.append(carry % output_base)
            carry //= output_base

    return converted[::-1]
