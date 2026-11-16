class CryptoMethodError(Exception):
    """Exception raised for errors in the encryption method."""
    pass


class CryptoKeyError(Exception):
    """Exception raised when an encryption/decryption key is missing or invalid."""
    pass
