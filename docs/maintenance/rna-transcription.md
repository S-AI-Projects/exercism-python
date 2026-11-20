# RNA Transcription test generation

The track's maintained generation inputs for this exercise are:

- `exercises/practice/rna-transcription/.meta/tests.toml`: enables or excludes
  canonical cases. All 6 canonical cases are enabled.
- `exercises/practice/rna-transcription/.meta/template.j2`: turns each enabled
  case into a `unittest` method and passes its `dna_strand` to `to_rna`.
- `config/generator_macros.j2`: supplies the generated-file header and imports.
- `.problem-specifications/exercises/rna-transcription/canonical-data.json`:
  canonical descriptions, inputs, and expected outputs.

`exercises/practice/rna-transcription/rna_transcription_test.py` is generated
from those inputs. `exercises/practice/rna-transcription/.meta/config.json`,
`exercises/practice/rna-transcription/.meta/example.py`, and the learner
solution module are maintained by hand. The reference example is used to verify
the generated tests, not as a generator input.

From the Python track repository root, regenerate the exercise test module with:

```sh
bin/generate_tests.py rna-transcription --spec-path .problem-specifications
```

This is the exercise-specific form of the CI generator entry point,
`bin/generate_tests.py --verbose -p .problem-specifications --check`. The
problem-specifications checkout and packages in `requirements-generator.txt`
(including Jinja2 and Black) are prerequisites.

## Case-to-output mapping

The table maps each named source case to the generated method in
`rna_transcription_test.py`; each generated method asserts `to_rna(value)`
equals the canonical expected value.

| Canonical description in `tests.toml` | Generated method | Input `dna_strand` | Expected output |
| --- | --- | --- | --- |
| Empty RNA sequence | `test_empty_rna_sequence` | `""` | `""` |
| RNA complement of cytosine is guanine | `test_rna_complement_of_cytosine_is_guanine` | `"C"` | `"G"` |
| RNA complement of guanine is cytosine | `test_rna_complement_of_guanine_is_cytosine` | `"G"` | `"C"` |

## Focused regeneration check

Run `python3 tools/course_checks/r36-t002.py` from the repository root to
regenerate the test module in two fresh temporary copies and compare the
results. It allows only the generated `# File last updated on YYYY-MM-DD`
header line to vary. The check asserts that all 6 enabled methods and the
three mapped methods are present. It does not modify the working tree.
