import os

from ..cipher.aes import AES
from ..cipher.rsa import RSA
from ..exceptions import CryptoKeyError


def generate_symmetric_key(length: int = 16) -> str:
    # Generate kunci simetris acak dalam format hex (default 16 bytes -> 32 char hex)
    return os.urandom(length).hex()


def generate_rsa_keys(bits: int = 2048):
    # Generate pasangan public key dan private key RSA
    return RSA.generate_keys(bits)


def _get_master_key(master_key=None) -> str:
    return (
        master_key
        or os.environ.get("MASTER_KEY")
        or os.environ.get("ENCRYPTION_KEY", "1234567890123456")
    )


def wrap_key(sym_key: str, master_key=None) -> str:
    if not sym_key:
        raise CryptoKeyError("Symmetric key tidak boleh kosong")

    # Bungkus symmetric key pakai Master Key dari .env agar aman disimpan di database
    kek = _get_master_key(master_key)
    return AES(kek).encrypt(sym_key)


def unwrap_key(wrapped_key: str, master_key=None) -> str:
    if not wrapped_key:
        raise CryptoKeyError("Wrapped key tidak boleh kosong")

    # Buka kembali symmetric key dari database pakai Master Key
    kek = _get_master_key(master_key)
    return AES(kek).decrypt(wrapped_key)


def encrypt_key_rsa(sym_key: str, public_key: str) -> str:
    # Enkripsi symmetric key memakai RSA public key penerima (untuk dikirim via WA/Email)
    return RSA(public_key).encrypt(sym_key)


def decrypt_key_rsa(encrypted_key: str, private_key: str) -> str:
    # Dekripsi symmetric key memakai RSA private key penerima
    return RSA(private_key).decrypt(encrypted_key)


def encrypt_file(raw_bytes: bytes, key: str) -> bytes:
    # Enkripsi bytes file (gambar/dokumen) pakai AES
    return AES(key).encrypt_bytes(raw_bytes)


def decrypt_file(encrypted_bytes: bytes, key: str) -> bytes:
    # Dekripsi bytes file (gambar/dokumen) pakai AES
    return AES(key).decrypt_bytes(encrypted_bytes)
