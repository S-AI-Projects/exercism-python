# Hints

## Python Guidance for Circular Buffer

### Iteration & Modulo Indexing
A circular buffer maintains two pointers: `read_point` and `write_point`. When advancing either pointer past the end of the backing store, use the modulo operator:
```python
next_pos = (current_pos + 1) % capacity
```
This ensures ring-wrap without reallocating or shifting elements.

### In-Place Mutation vs. Copying
Modifying buffer elements in-place (e.g. using a pre-allocated fixed-size `list` or [`bytearray`](https://docs.python.org/3/library/stdtypes.html#bytearray)) avoids the $\mathcal{O}(n)$ memory-copy overhead associated with inserting or popping from the front of standard Python lists. For alternative high-performance queueing, see [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque).

### Custom Exception Handling
The exercise requires two custom exception types: `BufferEmptyException` and `BufferFullException`. Subclassing built-in [`BufferError`](https://docs.python.org/3/library/exceptions.html#BufferError) or [`Exception`](https://docs.python.org/3/tutorial/errors.html) allows callers to catch domain-specific errors:
```python
class BufferEmptyException(BufferError):
    pass

class BufferFullException(BufferError):
    pass
```

### Runnable Micro-Example
```python
class TinyRing:
    def __init__(self, size):
        self.size = size
        self.buf = [None] * size
        self.r = self.w = 0

    def push(self, val):
        self.buf[self.w] = val
        self.w = (self.w + 1) % self.size

    def pop(self):
        val = self.buf[self.r]
        self.buf[self.r] = None
        self.r = (self.r + 1) % self.size
        return val

b = TinyRing(2)
b.push('A')
b.push('B')
print(b.pop(), b.pop())
```

**Expected Output:**
```
A B
```
