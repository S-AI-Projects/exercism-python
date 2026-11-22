# Hints

## General

- An acronym is formed by concatenating the first letter of each word in a phrase, in uppercase.
- Look at the Python `str` methods: `str.split()`, `str.replace()`, and `str.upper()`.
- Alternatively, Python's regular expressions module (`re`) can match word patterns directly using `re.findall()`.

---

## Input / Output Walkthrough for Key Contract Cases

The specification defines specific rules for how delimiters, casing, and punctuation interact:

### 1. Basic Title Case (`test_basic`)
- **Input:** `"Portable Network Graphics"`
- **Python Representation:** Standard `str` consisting of capitalized words separated by single spaces.
- **Walkthrough:**
  1. Splitting on whitespace yields three words: `["Portable", "Network", "Graphics"]`.
  2. The initial character of each word is extracted: `'P'`, `'N'`, `'G'`.
  3. All initials are already uppercase, so joining them gives `"PNG"`.
- **Expected Output:** `"PNG"`

### 2. Lowercase Words (`test_lowercase_words`)
- **Input:** `"Ruby on Rails"`
- **Python Representation:** `str` with mixed casing, including a lowercase preposition (`"on"`).
- **Walkthrough:**
  1. Splitting on whitespace yields: `["Ruby", "on", "Rails"]`.
  2. The initial character of each word is extracted: `'R'`, `'o'`, `'R'`.
  3. Casing must be normalized: `'o'.upper()` becomes `'O'`.
  4. Joining the uppercase initials produces `"ROR"`.
- **Expected Output:** `"ROR"`

### 3. Punctuation Handling (`test_punctuation`)
- **Input:** `"First In, First Out"`
- **Python Representation:** `str` containing non-hyphen punctuation (a comma `,` directly attached to `"In,"`).
- **Walkthrough:**
  1. Non-hyphen punctuation is removed or ignored during tokenization.
  2. The words identified are `["First", "In", "First", "Out"]`.
  3. Extracting the first letter of each word yields `'F'`, `'I'`, `'F'`, `'O'`.
  4. Joining uppercase characters produces `"FIFO"`.
- **Expected Output:** `"FIFO"`

---

## Contract Decision Table

The table below outlines how different input conditions map to required processing rules and expected outcomes:

| Input Pattern / Condition | Delimiter Rule | Casing Normalization | Non-Hyphen Punctuation | Word Order | Example Input | Expected Output |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Standard capitalized words** | Single space splits words | None needed | None | Left-to-right | `"Portable Network Graphics"` | `"PNG"` |
| **Mixed casing with lowercase** | Single space splits words | Lowercase initial converted to uppercase (`.upper()`) | None | Left-to-right | `"Ruby on Rails"` | `"ROR"` |
| **Trailing word punctuation** | Space splits words | None needed | Punctuation (`,` `!`) stripped from word | Left-to-right | `"First In, First Out"` | `"FIFO"` |
| **Hyphenated compound words** | Hyphen (`-`) treated as word delimiter | None needed | Hyphen acts as separator | Left-to-right | `"Complementary metal-oxide semiconductor"` | `"CMOS"` |
| **Consecutive / mixed delimiters** | Delimiters collapsed without empty words | None needed | Hyphens and spaces combined | Left-to-right | `"Something - I made up from thin air"` | `"SIMUFTA"` |
| **Apostrophe inside word** | Word kept intact | None needed | Apostrophe retained inside token (not a delimiter) | Left-to-right | `"Halley's Comet"` | `"HC"` |
| **Underscore emphasis** | Space splits words | None needed | Underscores (`_`) stripped, not treated as words | Left-to-right | `"The Road _Not_ Taken"` | `"TRNT"` |

---

## Specified vs. Unspecified Contract Boundaries

To keep implementations clean and robust without over-engineering:

### Specified Behavior (In-Contract)
- **Input Type:** Input is provided as a Python `str`.
- **Word Delimiters:** Whitespace characters and hyphens (`-`) separate words.
- **Punctuation Stripping:** Punctuation characters other than hyphens (such as commas, colons, exclamation points, periods, and underscores) are ignored and do not generate acronym letters.
- **Internal Apostrophes:** Apostrophes within contractions or possessives (e.g., `"Halley's"`) are part of the word and do not split it.
- **Case Normalization:** All letters in the final acronym must be uppercase.
- **Sequencing:** Acronym letters must follow the original left-to-right word order.

### Unspecified Behavior (Outside Contract)
- **No Unicode normalization:** The specification does not test or require special handling for non-ASCII Unicode characters or accented letters.
- **No numeric token handling:** The contract does not define behavior for numbers or mixed alphanumeric tokens (e.g., `"3D"`, `"MP3"`). Implementations should not introduce special digit coercions.
- **No custom exceptions or type validation:** The test suite does not require raising `TypeError` or `ValueError` for empty strings or non-string arguments. Do not add unrequested validation or error handling.
