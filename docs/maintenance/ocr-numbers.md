# OCR Numbers test generation

The generated suite follows this path:

1. `exercises/practice/ocr-numbers/.meta/tests.toml` selects canonical cases by
   UUID and includes only entries marked for this Python exercise.
2. `exercises/practice/ocr-numbers/.meta/template.j2` maps each selected case's
   description to a snake-case `test_...` method and renders its input and
   expected result.
3. `config/generator_macros.j2` supplies the generated-file header and imports.
4. `bin/generate_tests.py` reads
   `problem-specifications/exercises/ocr-numbers/canonical-data.json`, renders
   the template, formats the result with Black, and writes
   `exercises/practice/ocr-numbers/ocr_numbers_test.py`.

From a track checkout with `exercism/problem-specifications` cloned at
`.problem-specifications`, the maintained command is:

```sh
python3 bin/generate_tests.py --spec-path .problem-specifications ocr-numbers
```

The relevant case-to-output mapping is:

| Generated test | Input | Expected result |
| --- | --- | --- |
| `test_recognizes_0` | canonical 3-by-4 glyph for zero | `0` |
| `test_recognizes_1` | canonical 3-by-4 glyph for one | `1` |
| `test_unreadable_but_correctly_sized_inputs_return` | correctly sized but unrecognized glyph | `?` |
| `test_input_with_a_number_of_lines_that_is_not_a_multiple_of_four_raises_an_error` | three rows | `ValueError: Number of input lines is not a multiple of four` |
| `test_input_with_a_number_of_columns_that_is_not_a_multiple_of_three_raises_an_error` | four columns | `ValueError: Number of input columns is not a multiple of three` |
| `test_recognizes_110101100` | nine OCR glyphs | `110101100` |
| `test_garbled_numbers_in_a_string_are_replaced_with` | mixed valid and garbled glyphs | `11?10?1?0` |
| `test_recognizes_2` through `test_recognizes_9` | one canonical glyph per test | the corresponding digit, 2 through 9 |
| `test_recognizes_string_of_decimal_numbers` | ten adjacent glyphs | `1234567890` |
| `test_numbers_separated_by_empty_lines_are_recognized_lines_are_joined_by_commas` | three four-row groups | `123,456,789` |

At the recorded canonical-data revision the generated file contains 17 tests.
The focused task check regenerates twice in separate temporary trees, normalizes
only the date in the generated header, substitutes the reference only in those
trees, and runs all 17 cases. It writes the command output and tool versions to
`work/R36-T042/results.json`.
