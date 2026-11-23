from itertools import cycle
import random
from string import ascii_lowercase
from time import time


class Cipher:
    """
    Cipher handles substitution cipher operations over lowercase English alphabets.
    Invariant: Every character in self.key is lowercase ASCII ('a'..'z'), and for any
    alphabetic text, decode(encode(text)) == text with shifts applied modulo 26.
    """

    def __init__(self, key=None):
        # Invariant: key consists of lowercase ASCII letters; if not provided,
        # generate 100 pseudo-random lowercase characters.
        if key is None:
            random.seed(time())
            key = "".join(random.choice(ascii_lowercase) for _ in range(100))
        self.key = key

    def _shift(self, character, key_char, direction=1):
        # Invariant: Shift offsets are calculated relative to 'a' (0..25) modulo 26,
        # preserving the property that encode (direction=1) and decode (direction=-1)
        # are exact inverse operations.
        char_val = ord(character) - ord("a")
        shift_val = ord(key_char) - ord("a")
        new_val = (char_val + direction * shift_val) % 26
        return chr(ord("a") + new_val)

    def encode(self, text):
        return "".join(
            self._shift(character, key, direction=1)
            for character, key in zip(text, cycle(self.key))
        )

    def decode(self, text):
        return "".join(
            self._shift(character, key, direction=-1)
            for character, key in zip(text, cycle(self.key))
        )
