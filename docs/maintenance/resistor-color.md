# Maintenance: Resistor Color Test Generation

## Overview
This document specifies the test generation route, input dependencies, and reproducibility verification for the `resistor-color` exercise (`exercises/practice/resistor-color`).

## Generation Route & Command
The exercise test suite is generated from canonical problem specifications using Jinja2 templates:

```bash
python3 bin/generate_tests.py resistor-color
```

### Input Files
1. **Canonical Data:** `.problem-specifications/exercises/resistor-color/canonical-data.json`
2. **Template:** `exercises/practice/resistor-color/.meta/template.j2`
3. **Filter/Configuration:** `exercises/practice/resistor-color/.meta/tests.toml`
4. **Macros:** `config/generator_macros.j2`
5. **Config Metadata:** `exercises/practice/resistor-color/.meta/config.json`

### Output File
- `exercises/practice/resistor-color/resistor_color_test.py`

## Case-to-Output Mapping
The test generator iterates through the canonical cases and maps them as defined in `template.j2`:

| Canonical UUID | Description | Generated Test Name | Property / Input | Expected Result |
|---|---|---|---|---|
| `49eb31c5-10a8-4180-9f7f-fea632ab87ef` | Black | `test_black` | `color_code("black")` | `0` |
| `0a4df94b-92da-4579-a907-65040ce0b3fc` | White | `test_white` | `color_code("white")` | `9` |
| `5f81608d-f36f-4190-8084-f45116b6f380` | Orange | `test_orange` | `color_code("orange")` | `3` |
| `581d68fa-f968-4be2-9f9d-880f2fb73cf7` | Colors | `test_colors` | `colors()` | `["black", "brown", "red", "orange", "yellow", "green", "blue", "violet", "grey", "white"]` |

## Reproducibility & Timestamp Normalization
When regenerating test suites across different runs or days, the only permitted difference is the header timestamp comment:
```python
# File last updated on <YYYY-MM-DD>
```
After normalizing this single timestamp line (replacing the date or omitting the comment line during comparison), successive generations produce strictly identical byte-for-byte output with zero dropped cases.
