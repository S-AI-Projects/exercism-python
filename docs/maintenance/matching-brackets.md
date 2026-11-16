# Matching Brackets mutation check

The contract accepts only correctly matched and nested pairs of `[]`, `{}`,
and `()`. Non-bracket characters are ignored. A closing bracket must have a
preceding opening bracket of the same kind; it cannot be accepted merely
because it is a closing delimiter.

For a deliberate scratch mutation, change the empty-stack branch in the
maintained reference from `return False` to `return True`. This mutation accepts
a closer when no opener is available. The existing case
`test_wrong_ordered_brackets` rejects it with input `}{` and expected result
`False`. Reducing that input gives `}`; it is the smallest input that exposes
the mutation, and its expected result is still `False`.

The mutation exists only in a temporary exercise copy created by
`work/R36-T013/check.py`. The maintained reference correctly returns `False`
for both diagnostic inputs, and the learner solution remains unchanged.
