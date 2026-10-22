import os

from ..cipher.crypto import Crypto
from ..cipher.aes import AES
from ..cipher.des import DES
from ..cipher.rc4 import RC4
from ..exceptions import CryptoMethodError
import json

from .get_cipher import get_cipher

def decrypt_data(encrypted_data: dict) -> dict:
    cipher = get_cipher() 

    # Decrypt the data
    decrypted_json = cipher.decrypt(encrypted_data)

    # Convert JSON string back to dictionary
    decrypted_data = json.loads(decrypted_json)

    return decrypted_data 
