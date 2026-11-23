# Hints

## Markdown Contract Decisions & Walkthrough

### Contract Decision Table

| Test Case | Markdown Input | Specified HTML Output | Matched Contract Rule | Unspecified / Out-of-Scope Behavior |
|---|---|---|---|---|
| `test_parses_normal_text_as_a_paragraph` | `"This will be a paragraph"` | `"<p>This will be a paragraph</p>"` | Any line not prefixed by header (`#`) or list (`*`) is wrapped in `<p>...</p>`. | Multiline paragraphs and explicit line-break tags (`<br>`) are not evaluated. |
| `test_parsing_italics` | `"_This will be italic_"` | `"<p><em>This will be italic</em></p>"` | Text surrounded by single underscores (`_text_`) is replaced with `<em>text</em>`. | Escaped underscores (`\_`) or mid-word intra-token underscores are outside the contract. |
| `test_parsing_bold_text` | `"__This will be bold__"` | `"<p><strong>This will be bold</strong></p>"` | Text surrounded by double underscores (`__text__`) is replaced with `<strong>text</strong>`. | Processing order matters: double underscores (`__`) must be evaluated prior to single underscores (`_`) to avoid partial matching. |

### Subtle Contract Nuances
1. **Ordering of Delimiters:** Because `__` contains `_`, scanning or substituting bold text (`__...__` -> `<strong>...</strong>`) before italic text (`_..._` -> `<em>...</em>`) ensures that bold delimiters are not prematurely consumed as multiple empty italics.
2. **Tag Wrapping Scope:** Text-level inline styling (`<em>`, `<strong>`) applies inside paragraph tags (`<p>`), header tags (`<h1>`..`<h6>`), or list elements (`<li>`).
3. **Unspecified Elements:** The specification explicitly does not require supporting Markdown links, tables, blockquotes, or raw HTML passthrough.
