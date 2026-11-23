import secrets


def modular_pow(base, exp, mod):
    """Square-and-multiply algorithm for modular exponentiation."""
    res = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            res = (res * base) % mod
        base = (base * base) % mod
        exp //= 2
    return res


def private_key(p):
    # Use CSPRNG for cryptographic key generation
    return secrets.SystemRandom().randint(2, p - 1)


def public_key(p, g, private):
    return modular_pow(g, private, p)


def secret(p, public, private):
    return modular_pow(public, private, p)
