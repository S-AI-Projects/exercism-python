from string import ascii_lowercase


BLOCK_SIZE = 5
trtbl = str.maketrans(ascii_lowercase, ascii_lowercase[::-1])


# Complexity invariant:
# base_trans operates in O(N) time and O(N) auxiliary space where N = len(text).
# It filters alphanumeric characters in one pass O(N), converts to lowercase in O(K),
# and translates characters via the precompiled 256-entry table trtbl in O(K), where K <= N.
def base_trans(text):
    return ''.join([character for character in text if character.isalnum()]).lower().translate(trtbl)


def encode(plain):
    cipher = base_trans(plain)
    return ' '.join(cipher[idx:idx + BLOCK_SIZE]
                     for idx in range(0, len(cipher), BLOCK_SIZE))


def decode(ciphered):
    return base_trans(ciphered)
