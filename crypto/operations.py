import os

from .cipher.crypto import Crypto
from .cipher.aes import AES
from .cipher.des import DES
from .cipher.rc4 import RC4
from .exceptions import CryptoMethodError
import json

def get_cipher():
    method = os.environ.get("ENCRYPTION_METHOD", "AES").upper()
    key = os.environ.get("ENCRYPTION_KEY", "default_key")

    if method == "AES":
        # kalau gaada key di environment, pakai default key 16 bytes
        key = os.environ.get("ENCRYPTION_KEY", "1234567890123456")  
        return AES(key)
    elif method == "DES":
        key = os.environ.get("ENCRYPTION_KEY", "12345678")  # default key 8 bytes
        return DES(key)
    elif method == "RC4":
        key = os.environ.get("ENCRYPTION_KEY", "1234567890123456")  # default key
        return RC4(key)
    
    else:
        raise CryptoMethodError(f"Metode enkripsi tidak dikenal: {method}")

def encrypt_data(data: dict) -> dict:
    cipher = get_cipher() 

    json_data = json.dumps(data)

    # Encrypt the JSON string
    encrypted_data = cipher.encrypt(json_data)

    return encrypted_data

def decrypt_data(encrypted_data: dict) -> dict:
    cipher = get_cipher() 

    # Decrypt the data
    decrypted_json = cipher.decrypt(encrypted_data)

    # Convert JSON string back to dictionary
    decrypted_data = json.loads(decrypted_json)

    return decrypted_data 
