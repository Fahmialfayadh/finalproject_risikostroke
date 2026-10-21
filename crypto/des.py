import base64
from Crypto.Cipher import DES as DESCipher
from Crypto.Util.Padding import pad, unpad

from .crypto import Crypto


class DES(Crypto):
    def __init__(self, key):
        super().__init__(key)
        # Normalisasi kunci ke bytes dan pastikan panjang tepat 8 bytes (64-bit)
        if isinstance(key, str):
            key = key.encode('utf-8')
        if len(key) != 8:
            # Potong atau pad agar tepat 8 bytes
            key = key.ljust(8, b'0')[:8]
            
        self.key = key
        self.block_size = DESCipher.block_size  # 8 bytes

    def encrypt(self, data: str) -> str:
        cipher = DESCipher.new(self.key, DESCipher.MODE_CBC)
        padded_data = pad(data.encode('utf-8'), self.block_size)

        ciphertext = cipher.encrypt(padded_data)
        
        # Gabungkan IV (8 bytes) + Ciphertext (bytes)
        raw_result = cipher.iv + ciphertext
        
        return base64.b64encode(raw_result).decode('utf-8')

    def decrypt(self, data: str) -> str:
        raw_data = base64.b64decode(data)
        
        # Ekstrak IV (8 bytes pertama untuk DES) dan ciphertext
        iv = raw_data[:8]
        ct = raw_data[8:]
        
        cipher = DESCipher.new(self.key, DESCipher.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), self.block_size)
        
        return pt.decode('utf-8')