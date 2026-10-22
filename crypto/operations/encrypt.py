import os

from ..cipher.crypto import Crypto
from ..cipher.aes import AES
from ..cipher.des import DES
from ..cipher.rc4 import RC4
from ..exceptions import CryptoMethodError
import json

from .get_cipher import get_cipher

def encrypt_data(data: dict) -> dict:
    cipher = get_cipher() 

    json_data = json.dumps(data)

    # Encrypt the JSON string
    encrypted_data = cipher.encrypt(json_data)

    return encrypted_data
