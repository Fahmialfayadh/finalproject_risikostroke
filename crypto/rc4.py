import base64
from Crypto.Cipher import ARC4

from .crypto import Crypto


class RC4(Crypto):
    def __init__(self, key):
        super().__init__(key)

        # normalisasi kunci ke bytes (panjang fleksibel, misal 5 sampai 256 bytes)
        if isinstance(key, str):
            key = key.encode('utf-8')
        if len(key) == 0:
            key = b'default_rc4_key'
            
        self.key = key

    def encrypt(self, data: str) -> str:
        cipher = ARC4.new(self.key)
        ciphertext = cipher.encrypt(data.encode('utf-8'))
        
        return base64.b64encode(ciphertext).decode('utf-8')

    def decrypt(self, data: str) -> str:
        raw_data = base64.b64decode(data)
        cipher = ARC4.new(self.key)
        pt = cipher.decrypt(raw_data)
        
        return pt.decode('utf-8')