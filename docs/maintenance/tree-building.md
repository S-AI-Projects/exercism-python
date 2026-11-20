# Tree Building canonical case notes

The three reviewed canonical cases are included in `.meta/tests.toml`. Their
Python coverage and the reference operation that determines the result are:

| UUID | Canonical case | Python test | Rationale |
| --- | --- | --- | --- |
| `761790a3-4c27-461a-b4e9-8bce8ccee5a1` | empty list | `test_empty_list_input` | `sorted(...)` yields no IDs, so the construction loop never changes `root` from `None`. |
| `dcc89dc3-eb39-4f26-a3cd-964e607c95ff` | single record | `test_one_node` | `(0, 0)` is accepted by `validate_record`; the root branch selects `node_dict[0]`. |
| `dcdb80f0-e5da-43e1-8b8d-6f307be89c0e` | three records in order | `test_three_nodes_in_order` | Sorted IDs satisfy the `enumerate`/index check; each non-root record is appended to its parent. |

At this revision the canonical TOML has 16 entries and zero explicit
exclusions. The checked-in generated test module has 13 test methods. The
other three entries (`one root node and has parent`, `duplicate node`, and
`duplicate root`) have no corresponding method in that module. This review
does not change their `include` values: a metadata-only edit cannot add
generated coverage or establish a changed contract. No UUID is excluded in
the reviewed metadata, so there is no excluded case to characterize as
unsupported or replaced.

Run the isolated reference check with:

```bash
python3 work/R36-T011/check.py
```

The script copies the whole exercise, including dotfiles, into a temporary
directory, substitutes `.meta/example.py` for the solution there, and runs
the configured test module. It writes input and result summaries, captured
pytest output, and tool versions beside itself.
