# Space Age: Test Generation Route & Reproducibility

This document details the test generation route, input specifications, case mappings, and reproducibility verification for the `space-age` exercise in the Exercism Python track (Task R36-T022).

---

## 1. Generation Command & CLI Entry Point

The Exercism Python track uses `bin/generate_tests.py` with Jinja2 templates (`.meta/template.j2`) and canonical data from `exercism/problem-specifications` to generate test suites.

### Exact Generation Command
From the repository root:
```bash
python3 bin/generate_tests.py space-age
```
Or pointing to an explicit problem-specifications directory:
```bash
python3 bin/generate_tests.py -p .problem-specifications space-age
```

### Verification / Check Command (CI)
To verify that the existing test file matches the canonical template render without rewriting disk:
```bash
python3 bin/generate_tests.py --check space-age
```

---

## 2. Input Files & File Roles

The generation pipeline relies on four primary inputs:

1. **Canonical Data (`canonical-data.json`)**:
   - Location: `.problem-specifications/exercises/space-age/canonical-data.json`
   - Role: Defines standard canonical test cases, UUIDs, descriptions, inputs (`planet`, `seconds`), and expected orbital age outputs across all Exercism tracks.
2. **Track Test Inclusions (`tests.toml`)**:
   - Location: `exercises/practice/space-age/.meta/tests.toml`
   - Role: Controls which canonical test UUIDs are included or excluded in the Python track test suite.
3. **Jinja2 Test Template (`template.j2`)**:
   - Location: `exercises/practice/space-age/.meta/template.j2`
   - Role: Formats canonical test data into Python `unittest.TestCase` methods adhering to Python track idioms.
4. **Global Macros (`generator_macros.j2`)**:
   - Location: `config/generator_macros.j2`
   - Role: Standardizes file headers, canonical reference comments, timestamp formatting, and imports.

### Generated vs. Hand-Maintained Files

| File Path | Classification | Description |
| :--- | :--- | :--- |
| `exercises/practice/space-age/space_age_test.py` | **Generated** | Rendered by `bin/generate_tests.py` via `template.j2` and formatted with `black`. Do not hand-edit. |
| `exercises/practice/space-age/space_age.py` | **Hand-Maintained** | Learner starting stub (`class SpaceAge: def __init__(self, seconds): pass`). Must remain unsolved. |
| `exercises/practice/space-age/.meta/example.py` | **Hand-Maintained** | Reference solution used to validate track test suites. |
| `exercises/practice/space-age/.meta/tests.toml` | **Hand-Maintained** | Metadata tracking canonical UUID inclusion/exclusion decisions. |
| `exercises/practice/space-age/.meta/template.j2` | **Hand-Maintained** | Template mapping canonical cases to Python test methods. |
| `exercises/practice/space-age/.meta/config.json` | **Hand-Maintained** | Exercise configuration, file mapping, authors, and metadata. |
| `exercises/practice/space-age/.docs/*.md` | **Hand-Maintained** | Exercise problem description and instructions. |

---

## 3. Case-to-Output Mapping Table

All 9 canonical cases from `problem-specifications` are mapped below:

| Canonical UUID | Canonical Description | Input (`planet`, `seconds`) | Expected | Generated Test Method | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `84f609af-5a91-4d68-90a3-9e32d8a5cd34` | age on Earth | `"Earth"`, `1000000000` | `31.69` | `test_age_on_earth` | **Included** | Base earth orbital period ($31,557,600\text{ s}$). Anchored case 1. |
| `ca20c4e9-6054-458c-9312-79679ffab40b` | age on Mercury | `"Mercury"`, `2134835688` | `280.88` | `test_age_on_mercury` | **Included** | Orbital period $0.2408467\times$ Earth. Anchored case 2. |
| `502c6529-fd1b-41d3-8fab-65e03082b024` | age on Venus | `"Venus"`, `189839836` | `9.78` | `test_age_on_venus` | **Included** | Orbital period $0.61519726\times$ Earth. Anchored case 3. |
| `9ceadf5e-a0d5-4388-9d40-2c459227ceb8` | age on Mars | `"Mars"`, `2129871239` | `35.88` | `test_age_on_mars` | **Included** | Orbital period $1.8808158\times$ Earth. |
| `42927dc3-fe5e-4f76-a5b5-f737fc19bcde` | age on Jupiter | `"Jupiter"`, `901876382` | `2.41` | `test_age_on_jupiter` | **Included** | Orbital period $11.862615\times$ Earth. |
| `8469b332-7837-4ada-b27c-00ee043ebcad` | age on Saturn | `"Saturn"`, `2000000000` | `2.15` | `test_age_on_saturn` | **Included** | Orbital period $29.447498\times$ Earth. |
| `999354c1-76f8-4bb5-a672-f317b6436743` | age on Uranus | `"Uranus"`, `1210123456` | `0.46` | `test_age_on_uranus` | **Included** | Orbital period $84.016846\times$ Earth. |
| `80096d30-a0d4-4449-903e-a381178355d8` | age on Neptune | `"Neptune"`, `1821023456` | `0.35` | `test_age_on_neptune` | **Included** | Orbital period $164.79132\times$ Earth. |
| `57b96e2a-1178-40b7-b34d-f3c9c34e4bf4` | invalid planet causes error | `"Sun"`, `680804807` | `error` | *None* | **Excluded** | Excluded in `tests.toml` (`include = false`). See explanation below. |

---

## 4. Source of Anchored Cases

The three anchored cases are defined in `canonical-data.json` under `problem-specifications`:

1. **`test_age_on_earth`**:
   - **UUID:** `84f609af-5a91-4d68-90a3-9e32d8a5cd34`
   - **Assertion:** `self.assertEqual(SpaceAge(1000000000).on_earth(), 31.69)`
   - **Operation:** $\frac{1,000,000,000}{31,557,600} \approx 31.6877 \to 31.69$.
2. **`test_age_on_mercury`**:
   - **UUID:** `ca20c4e9-6054-458c-9312-79679ffab40b`
   - **Assertion:** `self.assertEqual(SpaceAge(2134835688).on_mercury(), 280.88)`
   - **Operation:** $\frac{2,134,835,688}{31,557,600 \times 0.2408467} \approx 280.88$.
3. **`test_age_on_venus`**:
   - **UUID:** `502c6529-fd1b-41d3-8fab-65e03082b024`
   - **Assertion:** `self.assertEqual(SpaceAge(189839836).on_venus(), 9.78)`
   - **Operation:** $\frac{189,839,836}{31,557,600 \times 0.61519726} \approx 9.78$.

### Rationale for Excluded Case (`57b96e2a-1178-40b7-b34d-f3c9c34e4bf4`)
Canonical case `57b96e2a-1178-40b7-b34d-f3c9c34e4bf4` ("invalid planet causes error") tests calling an age calculation with an unrecognized planet string like `"Sun"`. In the Python track, the API design exposes individual methods on the `SpaceAge` instance (`on_earth()`, `on_mercury()`, `on_venus()`, etc.) rather than a parameterized function accepting a planet string. Thus, an invalid planet string is structurally impossible to pass to this API, and the test is marked `include = false` in `.meta/tests.toml`.

---

## 5. Timestamp Normalization & Generation Determinism

When `bin/generate_tests.py` runs, Jinja renders the canonical reference header from `config/generator_macros.j2`:

```python
# These tests are auto-generated with test data from:
# https://github.com/exercism/problem-specifications/tree/main/exercises/space-age/canonical-data.json
# File last updated on YYYY-MM-DD
```

Line 3 records `current_date` dynamically at generation time (`env.globals["current_date"] = datetime.now(tz=timezone.utc).date()`).

To achieve deterministic comparison across multiple generations:
- As documented and implemented in `bin/generate_tests.py:check_template` (lines 288–292), lines 1–3 are skipped or normalized when comparing generated files.
- The remaining content (lines 4 through 35, containing all imports, classes, and test cases) is 100% deterministic and byte-for-byte identical across independent generation runs.
- Automated checks (`tools/course_checks/r36-t022.py` and `work/R36-T022/check.py`) verify this exact normalization property.
