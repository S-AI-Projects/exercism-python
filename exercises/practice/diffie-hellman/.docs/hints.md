# Hints

## Approach Selection: Built-in `pow` vs Cryptographic `secrets` / Modular Exponentiation

When implementing Diffie-Hellman in Python, consider the following approaches:

### Approach 1: Built-in 3-Argument `pow()` with `random.randint` (Standard Reference)
- **Implementation:** `pow(g, private, p)` and `random.randint(2, p - 1)`.
- **Performance:** Implemented in C within CPython, running in $\mathcal{O}(\log(\text{private}))$ time with minimal memory overhead.
- **Trade-off:** `random.randint` uses the Mersenne Twister, which is fast and deterministic given a seed, but not cryptographically secure for real-world key exchanges.

### Approach 2: Cryptographically Secure `secrets` with Binary Exponentiation (Alternative)
- **Implementation:** `secrets.SystemRandom().randint(2, p - 1)` for key generation, with explicit square-and-multiply exponentiation:
  ```python
  def modular_pow(base, exp, mod):
      res = 1
      base = base % mod
      while exp > 0:
          if exp % 2 == 1:
              res = (res * base) % mod
          base = (base * base) % mod
          exp //= 2
      return res
  ```
- **Performance:** Slower in pure Python bytecode compared to C-level `pow()`, but illustrates the low-level bitwise mechanics of exponentiation by squaring.
- **Trade-off:** Provides true cryptographic entropy suitable for security protocols, but introduces minor overhead in tight loops.

### Small Worked Input
For prime $p = 23$, generator $g = 5$:
1. Alice chooses private key $a = 6 \in [2, 22]$.
   - Public key $A = 5^6 \pmod{23} = 15625 \pmod{23} = 8$.
2. Bob chooses private key $b = 15 \in [2, 22]$.
   - Public key $B = 5^{15} \pmod{23} = 19$.
3. Shared Secret:
   - Alice computes $B^a \pmod{23} = 19^6 \pmod{23} = 2$.
   - Bob computes $A^b \pmod{23} = 8^{15} \pmod{23} = 2$.
   - Both sides arrive at identical shared secret $s = 2$.
