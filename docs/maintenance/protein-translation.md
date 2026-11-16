# Protein Translation test generation

The track's maintained generation inputs for this exercise are:

- `exercises/practice/protein-translation/.meta/tests.toml`: enables or excludes
  canonical cases. The empty-strand case and invalid/incomplete-codon cases are
  explicitly excluded; the remaining 26 canonical cases are enabled.
- `exercises/practice/protein-translation/.meta/template.j2`: turns each enabled
  case into a `unittest` method and passes its `strand` to `proteins`.
- `config/generator_macros.j2`: supplies the generated-file header and imports.
- `.problem-specifications/exercises/protein-translation/canonical-data.json`:
  canonical descriptions, inputs, and expected outputs.

`exercises/practice/protein-translation/protein_translation_test.py` is generated
from those inputs. `exercises/practice/protein-translation/.meta/config.json`,
`exercises/practice/protein-translation/.meta/example.py`, and the learner
solution module are maintained by hand. The reference example is used to verify
the generated tests, not as a generator input.

From the Python track repository root, regenerate the exercise test module with:

```sh
bin/generate_tests.py protein-translation --spec-path .problem-specifications
```

This is the exercise-specific form of the CI generator entry point,
`bin/generate_tests.py --verbose -p .problem-specifications --check`. The
problem-specifications checkout and packages in `requirements-generator.txt`
(including Jinja2 and Black) are prerequisites.

## Case-to-output mapping

The table maps each named source case to the generated method in
`protein_translation_test.py`; each generated method asserts `proteins(value)`
equals the canonical expected value.

| Canonical description in `tests.toml` | Generated method | Input strand | Expected output |
| --- | --- | --- | --- |
| Methionine RNA sequence | `test_methionine_rna_sequence` | `AUG` | `['Methionine']` |
| Phenylalanine RNA sequence 1 | `test_phenylalanine_rna_sequence_1` | `UUU` | `['Phenylalanine']` |
| Phenylalanine RNA sequence 2 | `test_phenylalanine_rna_sequence_2` | `UUC` | `['Phenylalanine']` |

## Focused regeneration check

Run `python3 tools/course_checks/r36-t012.py` from the repository root to
regenerate the test module in two fresh temporary copies and compare the
results. It allows only the generated `# File last updated on YYYY-MM-DD`
header line to vary. The check asserts that all 26 enabled methods and the
three mapped methods are present. It does not modify the working tree.
