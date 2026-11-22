# Hints

## General

- A doubly linked list node must maintain references to both its next node (`succeeding`) and its previous node (`prev`).
- Keep track of both the `head` and `tail` pointers on the `LinkedList` instance to support $O(1)$ operations at both ends.

## Debugging: Multiple `pop()` Operations

- When removing an element from the tail using `pop()`, pay close attention to how you determine whether the list has become empty.
- Because the tail node is at the very end of the list, its forward link (`succeeding`) is always `None`, regardless of how many elements are currently stored in the list.
- If you check `succeeding is None` to decide whether to set `head` and `tail` to `None`, you will inadvertently clear the entire list on the first `pop()`, causing any subsequent `pop()` to fail unexpectedly.
- Instead, inspect the backward pointer (`prev`) on the tail node: if `node.prev is None`, the popped node was the only element in the list.

### Diagnostic Input

To test your pointer management when removing elements from the end, try this sequence:

```python
lst = LinkedList()
lst.push(1)
lst.push(2)

first = lst.pop()   # Should return 2, leaving 1 element in the list
second = lst.pop()  # Should return 1, leaving the list empty
```

If your code raises an error on the second `pop()`, check whether your tail removal logic prematurely set `self.tail = None` on the first call.
