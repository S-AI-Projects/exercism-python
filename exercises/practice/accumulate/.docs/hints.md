# Python hint: build a fresh result while iterating

`accumulate` applies an operation to each input value and returns a new
collection. Python's `for` statement visits the items in sequence order; a
separate list can collect each operation result with `append`. This is the
mutation/copying detail used by this exercise: do not append results to the
input list while iterating over it. The input should remain available as it was
given. The function also adds no exception-handling contract: if `operation`
raises an exception, it propagates to the caller.

<!-- r36-t047-example-start -->
```python
values = [1, 2, 3]
squares = []
for value in values:
    squares.append(value * value)
print(squares)
print(values)
```
<!-- r36-t047-example-end -->

Expected output:

```text
[1, 4, 9]
[1, 2, 3]
```

The input stays unchanged while results go into a separate list. See Python's
[tutorial on `for` statements and creating a new collection](https://docs.python.org/3.13/tutorial/controlflow.html#for-statements)
and the [list `append` method](https://docs.python.org/3.13/tutorial/datastructures.html#more-on-lists).
