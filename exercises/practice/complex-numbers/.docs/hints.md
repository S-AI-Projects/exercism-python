# Hints

## Python Representation of Complex Numbers

In this exercise, you implement a custom `ComplexNumber` class that represents complex numbers in Cartesian form: $z = a + bi$, where $a$ is the real part and $b$ is the imaginary component.

The constructor takes `(real, imaginary)` and exposes them as attributes or properties `real` and `imaginary`:

```python
class ComplexNumber:
    def __init__(self, real, imaginary):
        self.real = real
        self.imaginary = imaginary
```

## Contract Walkthrough for Real and Imaginary Part Extraction

The specification defines direct attribute access to the real and imaginary components. The following decision table outlines the exact inputs, expected outcomes, and behavioral rationale for the key contract cases:

### Decision Table

| Test Case Name | Input Arguments `(real, imaginary)` | Property Accessed | Expected Value | Contract Behavior & Rationale |
| --- | --- | --- | --- | --- |
| `test_real_part_of_a_purely_real_number` | `(1, 0)` | `.real` | `1` | A purely real number has $a = 1$ and $b = 0$. Accessing `.real` directly yields the real component $1$ without modification. |
| `test_real_part_of_a_purely_imaginary_number` | `(0, 1)` | `.real` | `0` | A purely imaginary number has $a = 0$ and $b = 1$. The real component is zero. |
| `test_real_part_of_a_number_with_real_and_imaginary_part` | `(1, 2)` | `.real` | `1` | A general complex number $1 + 2i$. Accessing `.real` isolates the first coordinate $1$. |

## Scope & Contract Boundaries

1. **Direct Component Access**: The `.real` property should reflect the value passed at initialization. Do not perform rounding, truncation, or implicit type coercion (e.g. converting `int` to `float` or vice-versa) unless specifically requested by arithmetic operations.
2. **Equality Contract**: Two complex numbers are equal if and only if their corresponding real and imaginary parts are equal: `self.real == other.real and self.imaginary == other.imaginary`.
3. **No Unspecified Errors**: Inputs satisfying numeric types (`int`, `float`) are valid. Do not impose custom ordering assertions or arbitrary error rules beyond what standard arithmetic and the canonical test suite specify.
