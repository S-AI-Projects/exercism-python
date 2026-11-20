# Pov mutation check

The `pov` exercise requires re-orienting a directed tree from the perspective of a chosen node (`from_pov`), making that node the root of the tree and reversing parent-child relationships along the path from the old root.

A critical contract requirement during re-rooting is that when a child node adopts its former parent, the former parent must have the child detached from its own list of children to prevent cycles and duplicate subtrees.

## Scratch Mutant

In a scratch copy of the reference implementation (`.meta/example.py`), modify the re-parenting step in `from_pov`:

```python
# Original:
stack.append(child.add(tree.remove(child.label)))

# Mutant:
stack.append(child.add(tree))
```

This mutation fails to remove `child` from `tree` before attaching `tree` as a child of `child`.

## Rejecting Test Case

The existing test case `test_can_reroot_a_tree_with_a_parent_and_one_sibling` rejects this mutant:
- Input tree: `Tree("parent", [Tree("x"), Tree("sibling")])`
- Call: `tree.from_pov("x")`
- Expected: `Tree("x", [Tree("parent", [Tree("sibling")])])`
- Mutant output: `Tree("x", [Tree("parent", [Tree("sibling"), Tree("x")])])`

The assertion fails because `parent` incorrectly retains `x` as a child node.

The mutation check is automated by `work/R36-T003/check.py`, which validates that the clean reference passes all 15 tests, the mutated copy fails the named assertion, and the learner stub remains unchanged.
