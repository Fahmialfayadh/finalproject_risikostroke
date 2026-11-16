import base64
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA as RSACipher

from .crypto import Crypto
from ..exceptions import CryptoKeyError


class RSA(Crypto):
    def __init__(self, key=None):
        super().__init__(key)
        # Import kunci RSA dalam format PEM jika diberikan
        if key is not None:
            if isinstance(key, str):
                key = key.encode('utf-8')
            try:
                self.key = RSACipher.import_key(key)
            except (ValueError, IndexError, TypeError):
                raise CryptoKeyError("Format kunci RSA tidak valid")
        else:
            self.key = None

    @staticmethod
    def generate_keys(bits: int = 2048):
        # Generate pasangan public key & private key dalam format PEM
        key = RSACipher.generate(bits)
        public_key = key.publickey().export_key().decode('utf-8')
        private_key = key.export_key().decode('utf-8')
        return public_key, private_key

    def encrypt(self, data: str) -> str:
        if self.key is None:
            raise CryptoKeyError("Public key RSA dibutuhkan untuk enkripsi")

        # Enkripsi data menggunakan public key dan padding OAEP
        cipher = PKCS1_OAEP.new(self.key.publickey())
        ciphertext = cipher.encrypt(data.encode('utf-8'))

        # Ubah ke Base64 string
        return base64.b64encode(ciphertext).decode('utf-8')

    def decrypt(self, data: str) -> str:
        if self.key is None or not self.key.has_private():
            raise CryptoKeyError("Private key RSA dibutuhkan untuk dekripsi")

        raw_data = base64.b64decode(data)

        try:
            cipher = PKCS1_OAEP.new(self.key)
            pt = cipher.decrypt(raw_data)
        except (ValueError, TypeError):
            raise CryptoKeyError("Dekripsi RSA gagal, pastikan private key sesuai")

        return pt.decode('utf-8')
