import os

from ..cipher.crypto import Crypto
from ..cipher.aes import AES
from ..cipher.des import DES
from ..cipher.rc4 import RC4
from ..cipher.rsa import RSA
from ..exceptions import CryptoMethodError
import json


def get_cipher(method=None, key=None):
    method = (method or os.environ.get("ENCRYPTION_METHOD", "AES")).upper()

    if method == "AES":
        # kalau gaada key di environment, pakai default key 16 bytes
        key = key or os.environ.get("ENCRYPTION_KEY", "1234567890123456")
        return AES(key)
    elif method == "DES":
        key = key or os.environ.get("ENCRYPTION_KEY", "12345678")  # default key 8 bytes
        return DES(key)
    elif method == "RC4":
        key = key or os.environ.get("ENCRYPTION_KEY", "1234567890123456")  # default key
        return RC4(key)
    elif method == "RSA":
        return RSA(key)

    else:
        raise CryptoMethodError(f"Metode enkripsi tidak dikenal: {method}")
