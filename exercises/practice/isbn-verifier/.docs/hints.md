# Hints

## General

- The ISBN-10 format is 9 digits (0 to 9) plus one check character (either a digit or `X`).
- When the check character is `X`, it represents the numerical value `10`.
- Hyphens (`-`) may appear anywhere as separators and should be stripped during preprocessing.
- The validation formula is:
  `(d₁ * 10 + d₂ * 9 + d₃ * 8 + d₄ * 7 + d₅ * 6 + d₆ * 5 + d₇ * 4 + d₈ * 3 + d₉ * 2 + d₁₀ * 1) % 11 == 0`
- If the result is 0 and the input conforms to the 10-character structure, the ISBN is valid.

## Python-Specific: Mutable Sequences vs. String Immutability

In Python, strings (`str`) are **immutable sequences**. Once a string is created, individual characters cannot be modified in place. Attempting item assignment such as `isbn[-1] = '10'` will raise a `TypeError: 'str' object does not support item assignment`.

### Why the Reference Implementation Converts to a Mutable List

The reference implementation in `.meta/example.py` preprocesses the input by converting the sanitized string into a mutable `list` of characters:

```python
chars = list(isbn.replace('-', ''))
if chars and chars[-1] == 'X':
    chars[-1] = '10'
```

Converting the string to a `list` provides two crucial benefits:
1. **Targeted In-Place Mutation:** It allows mutating *only* the final element (`chars[-1] = '10'`) in place if it is `'X'`, without affecting any preceding characters.
2. **Preserving Length:** The length of the list remains exactly 10 (`len(chars) == 10`), even though the element `'10'` contains two digits.

#### Executable Micro-Example: Targeted List Mutation

```python
# Convert immutable string to mutable list for selective check-digit assignment
raw = "012345678X"
chars = list(raw)
if chars and chars[-1] == "X":
    chars[-1] = "10"

print(chars)
# Expected output: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '10']
print(len(chars))
# Expected output: 10
```

### Exercise-Relevant Pitfall: String Copy Replacement (`str.replace`)

A common mistake is using `isbn.replace('X', '10')` on the string directly. Because strings are immutable, `.replace()` returns a new string copy and replaces **all** occurrences of `'X'`. This introduces two severe bugs:

1. **Accepting Invalid Interior 'X' Characters:** If an `'X'` appears in an invalid non-terminal position (e.g. `"3-598-2X507-9"`), `.replace('X', '10')` will silently replace it, converting an invalid ISBN into digits and corrupting validation.
2. **Corrupting Sequence Length:** Substituting the 2-character string `'10'` into a string increases the string length from 10 to 11 (`len("01234567810") == 11`), which causes subsequent length checks (`len(...) == 10`) to fail for otherwise valid ISBNs ending in `'X'`.

#### Executable Micro-Example: Pitfall Demonstration

```python
# Pitfall: string .replace('X', '10') alters character count and replaces interior characters
bad_isbn = "35982X5079"
replaced = bad_isbn.replace("X", "10")

print(replaced)
# Expected output: "35982105079"
print(len(replaced))
# Expected output: 11
```

For more details on sequence mutability and operations, consult the official Python documentation:
- [Python Standard Library: Mutable Sequence Types (list)](https://docs.python.org/3/library/stdtypes.html#mutable-sequence-types)
- [Python Standard Library: Text Sequence Type (str)](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)
