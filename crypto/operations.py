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

def decrypt_record(record):
    """
    Decrypts the encrypted payload of a StrokeRecord instance.
    Returns the decrypted data as a dictionary.
    """
    decrypted_records = []
    for r in record:
        payload = decrypt_data(r.encrypted_payload)
        decrypted_data = {
        "name": payload.get("name", ""),
        "age": float(payload.get("age", 0)),
        "weight": float(payload.get("weight", 0)),
        "height": float(payload.get("height", 1)),
        "glucose": float(payload.get("glucose", 0)),
        "gender": payload.get("gender", "Other"),
        "ever_married": payload.get("ever_married", "No"),
        "work_type": payload.get("work_type", "Private"),
        "residence": payload.get("residence", "Urban"),
        "smoking": payload.get("smoking", "Unknown"),
        "hypertension": int(payload.get("hypertension", 0)),
        "heart_disease": int(payload.get("heart_disease", 0)),
        }
        decrypted_records.append(decrypted_data)
        
    return decrypted_records
