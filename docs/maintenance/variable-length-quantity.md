# Variable Length Quantity Performance & Scaling Analysis

## Overview
This document explains the computational scaling and resource usage of `encode_single` in `exercises/practice/variable-length-quantity/.meta/example.py`.

## Algorithm & Invariant
`encode_single(number)` transforms a non-negative integer into a sequence of 7-bit payload bytes with the 8th bit acting as a continuation flag:
1. The least significant 7 bits are masked with `0x7F`. Its MSB (8th bit) is left `0` indicating the terminal byte.
2. The number is right-shifted by 7 bits (`number >>= 7`).
3. While `number > 0`, each subsequent 7-bit chunk has bit 7 set (`| 0x80`) as a continuation flag and appended.
4. The list is reversed to return big-endian order (`byte_string[::-1]`).

## Complexity Analysis

- **Time Complexity:** $\mathcal{O}(\lceil \log_{128}(N + 1) \rceil) = \mathcal{O}(\log N)$, where $N$ is the numerical value of the input. In terms of bit-length $b = \lfloor \log_2 N \rfloor + 1$, the time is $\mathcal{O}(b)$.
- **Space Complexity:** $\mathcal{O}(b / 7)$ bytes allocated in `byte_string`.
- **32-Bit Bound:** Since standard VLQ exercises operate on inputs up to 32 bits ($0 \le N \le 2^{32} - 1$), the loop executes at most 5 times, making runtime and memory strictly bounded by a small constant ($k \le 5$).

## Empirical Operation Trace Across Three Representative Cases

| Test Case | Input ($N$) | Bit-Length ($b$) | While Loop Iterations | Total Bytes Generated | Output Bytes |
|---|---|---|---|---|---|
| Single byte (`test_arbitrary_single_byte`) | `0x40` (64) | 7 bits | 0 | 1 | `[0x40]` |
| Double byte (`test_arbitrary_double_byte`) | `0x2000` (8192) | 14 bits | 1 | 2 | `[0xC0, 0x00]` |
| Triple byte (`test_arbitrary_triple_byte`) | `0x100000` (1048576) | 21 bits | 2 | 3 | `[0xC0, 0x80, 0x00]` |

### Detailed Step-by-Step Trace
1. **Case 1: $N = 0\text{x}40$ ($64_{10}$)**
   - `byte_string = [64 & 0x7F] = [0x40]`
   - `number >>= 7` $\implies number = 0$
   - Loop `while number > 0` does not execute (0 iterations).
   - Reversal: `[0x40]`.

2. **Case 2: $N = 0\text{x}2000$ ($8192_{10}$)**
   - `byte_string = [8192 & 0x7F] = [0x00]`
   - `number >>= 7` $\implies number = 64$
   - Iteration 1: `byte_string.append((64 & 0x7F) | 0x80) = [0x00, 0xC0]`, `number >>= 7` $\implies 0$.
   - Loop terminates (1 iteration).
   - Reversal: `[0xC0, 0x00]`.

3. **Case 3: $N = 0\text{x}100000$ ($1048576_{10}$)**
   - `byte_string = [1048576 & 0x7F] = [0x00]`
   - `number >>= 7` $\implies number = 8192$
   - Iteration 1: appends `(8192 & 0x7F) | 0x80 = 0x80`. `number >>= 7` $\implies 64$.
   - Iteration 2: appends `(64 & 0x7F) | 0x80 = 0xC0`. `number >>= 7` $\implies 0$.
   - Loop terminates (2 iterations).
   - Reversal: `[0xC0, 0x80, 0x00]`.

## Limits of Conclusion
The logarithmic complexity holds with respect to the magnitude of the number $N$. If measured with respect to input representation size (i.e. number of bits $b$), the complexity is strictly linear $\mathcal{O}(b)$.
