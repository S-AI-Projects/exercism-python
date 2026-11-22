# Linked List: Mutation-Driven Regression & Contract Analysis

This document details the mutation-driven regression verification for the `linked-list` exercise in the Exercism Python track (Task R36-T023).

---

## 1. Overview & Objective

The objective of this task is to create a small, deliberate mutant in a temporary copy of the reference implementation, identify which existing test case in the test suite rejects the mutant, and verify the contract boundaries of doubly linked list node manipulation.

- **Exercise:** `exercises/practice/linked-list`
- **Reference Solution:** `exercises/practice/linked-list/.meta/example.py`
- **Learner Stub:** `exercises/practice/linked-list/linked_list.py` (remains unsolved)
- **Total Test Cases:** 24 (16 canonical + 8 track-specific error/mutation tests)

---

## 2. Deliberate Mutation Specification

A common pitfall when implementing `pop()` in a doubly linked list is incorrectly identifying when the list has transitioned from a single-element list to an empty list.

### Original Reference Implementation (`.meta/example.py`)
```python
    def pop(self):
        node = self.tail

        if self.length == 0:
            raise IndexError("List is empty")
        if node is None or node.prev is None:
            self.head = self.tail = None
        else:
            self.tail = self.tail.prev
            self.tail.succeeding = None
        self.length -= 1

        return node.value
```

### Mutated Code (`pop()` condition mutation)
```python
    def pop(self):
        node = self.tail

        if self.length == 0:
            raise IndexError("List is empty")
        # MUTANT: Checking forward pointer 'succeeding' instead of backward pointer 'prev'
        if node is None or node.succeeding is None:
            self.head = self.tail = None
        else:
            self.tail = self.tail.prev
            self.tail.succeeding = None
        self.length -= 1

        return node.value
```

### Underlying Contract & Mistaken Assumption
- **Contract:** A node's `prev` attribute points to the preceding node in the list. When popping from `tail`, `node.prev is None` indicates that the current tail has no predecessor (i.e. it is the solitary node in the list, where `head == tail`).
- **Mistaken Assumption:** The author inadvertently inspects `node.succeeding is None` to check if the list becomes empty. However, on any tail node, `node.succeeding` is *always* `None`. Consequently, `node.succeeding is None` evaluates to `True` on every single call to `pop()`, prematurely destroying `self.head` and `self.tail` after popping just one item from a multi-element list.

---

## 3. Rejecting Test Case Identification

The test suite contains 3 relevant anchor cases:

1. **`test_pop_gets_element_from_the_list`** (UUID: `7f7e3987-b954-41b8-8084-99beca08752c`):
   - **Input:** `push(7)`, `pop()`
   - **Result on Mutant:** **PASSED** (Single-element list; clearing `head` and `tail` happens to be correct here).
2. **`test_shift_gets_an_element_from_the_list`** (UUID: `00ea24ce-4f5c-4432-abb4-cc6e85462657`):
   - **Input:** `push(17)`, `shift()`
   - **Result on Mutant:** **PASSED** (Operates through `shift()` from `head`, unaffected by `pop()`).
3. **`test_push_pop_respectively_add_remove_at_the_end_of_the_list`** (UUID: `c3f67e5d-cfa2-4c3e-a18f-7ce999c3c885`):
   - **Input:** `push(11)`, `push(13)`, `pop()`, `pop()`
   - **Result on Mutant:** **REJECTED (FAILED)**
   - **Failure Detail:**
     ```text
     E   AttributeError: 'NoneType' object has no attribute 'value'
     linked_list.py:70: AttributeError
     ```
     On the second pop (`lst.pop() == 11`), `self.tail` is unexpectedly `None`, triggering an `AttributeError`.

### Smallest Input Allowed by Specification
The minimal input sequence that exposes the regression is:
```python
lst = LinkedList()
lst.push(11)
lst.push(13)
lst.pop()  # Returns 13
lst.pop()  # Expected: 11; Actual with mutant: AttributeError (self.tail is None)
```
Pushing two elements and popping them in succession is the minimal contract sequence that verifies backward pointer persistence across multi-element removals.

---

## 4. Verification Results Summary

| Target | Test Suite | Executed | Passed | Failed | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Original Reference** | Full Suite | 24 | 24 | 0 | **PASS** |
| **Mutated Implementation** | Target Suite | 3 | 2 | 1 | **REJECTED (as expected)** |
| **Learner Stub** | Working Tree | N/A | N/A | N/A | **Unsolved** |

Automated verification is codified in `work/R36-T023/check.py` and run via Python subprocess in isolated temporary directories.
