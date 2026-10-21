import base64
from Crypto.Cipher import AES as AESCipher
from Crypto.Util.Padding import pad, unpad

from .crypto import Crypto


class AES(Crypto):
    def __init__(self, key):
        super().__init__(key)
        # Normalisasi kunci ke bytes dan pastikan panjang 16 bytes (128-bit)
        if isinstance(key, str):
            key = key.encode('utf-8')
        if len(key) not in (16, 24, 32):
            # Pad atau potong agar valid 16 bytes jika panjang tidak sesuai
            key = key.ljust(16, b'0')[:16]
            
        self.key = key
        self.block_size = AESCipher.block_size 

    def encrypt(self, data: str) -> str:
        # Generate cipher baru (IV otomatis dibuat acak oleh PyCryptodome)
        cipher = AESCipher.new(self.key, AESCipher.MODE_CBC)
        padded_data = pad(data.encode('utf-8'), self.block_size)

        ciphertext = cipher.encrypt(padded_data)
        
        # Gabungkan IV (16 bytes) + Ciphertext (bytes)
        raw_result = cipher.iv + ciphertext
        
        # Ubah ke Base64 string
        return base64.b64encode(raw_result).decode('utf-8')

    def decrypt(self, data: str) -> str:
        raw_data = base64.b64decode(data)
        
        # Ekstrak IV (16 bytes pertama) dan ciphertext
        iv = raw_data[:16]
        ct = raw_data[16:]
        
        cipher = AESCipher.new(self.key, AESCipher.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), self.block_size)
        
        return pt.decode('utf-8')