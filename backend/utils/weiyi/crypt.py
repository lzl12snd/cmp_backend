from io import BytesIO
from typing import Callable, Union

from Cryptodome import Random
from Cryptodome.Cipher.PKCS1_v1_5 import PKCS115_Cipher
from Cryptodome.PublicKey import RSA

Buffer = Union[bytes, bytearray, memoryview]


def batched(source: Buffer, size: int):
    for i in range(0, len(source), size):
        yield source[i : i + size]


class RsaCipher(PKCS115_Cipher):
    def __init__(
        self,
        key: RSA.RsaKey,
        randfunc: Callable[[int], bytes],
    ):
        self._key = key
        self._randfunc = randfunc

        # https://datatracker.ietf.org/doc/html/rfc8017#section-7.2
        # mLen: message octet length
        # k: key octet length
        # mLen <= k - 11
        self._key_length = key.size_in_bytes()
        self._message_length = self._key_length - 11

        super().__init__(self._key, self._randfunc)

    def encrypt(self, message: Buffer) -> bytes:
        buffer = BytesIO()
        for chunk in batched(message, self._message_length):
            buffer.write(super().encrypt(chunk))
        return buffer.getvalue()

    def decrypt(self, ciphertext: Buffer) -> bytes:
        buffer = BytesIO()
        for chunk in batched(ciphertext, self._key_length):
            buffer.write(super().decrypt(chunk, b""))
        return buffer.getvalue()

    @classmethod
    def new(cls, key: RSA.RsaKey):
        return cls(key, Random.get_random_bytes)
