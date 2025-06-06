"""Encryption utilities."""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_data(key: bytes, data: bytes) -> bytes:
    """Encrypt bytes using AES-GCM."""
    aes = AESGCM(key)
    nonce = b"0" * 12
    return aes.encrypt(nonce, data, None)


def decrypt_data(key: bytes, token: bytes) -> bytes:
    aes = AESGCM(key)
    nonce = b"0" * 12
    return aes.decrypt(nonce, token, None)
