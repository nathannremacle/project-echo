"""
Encryption utilities for credential storage
Uses AES-256 encryption for sensitive data
"""

import base64
import os
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


def _get_encryption_key() -> bytes:
    """Get or generate encryption key from settings"""
    encryption_key = settings.ENCRYPTION_KEY
    
    if not encryption_key:
        raise ValueError("ENCRYPTION_KEY not set in environment variables")
    
    if len(encryption_key) < 32:
        raise ValueError("ENCRYPTION_KEY must be at least 32 characters")
    
    # Use first 32 bytes for key derivation
    key_material = encryption_key[:32].encode('utf-8')
    
    # Derive key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'project_echo_salt',  # In production, use random salt stored separately
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(key_material))
    return key


def encrypt_value(value: str) -> str:
    """
    Encrypt a string value
    
    Args:
        value: Plain text value to encrypt
    
    Returns:
        Encrypted value as base64 string
    """
    if not value:
        return value
    
    try:
        key = _get_encryption_key()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(value.encode('utf-8'))
        return encrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise ValueError(f"Failed to encrypt value: {e}")


def decrypt_value(encrypted_value: str) -> str:
    """
    Decrypt an encrypted value
    
    Args:
        encrypted_value: Encrypted value as base64 string
    
    Returns:
        Decrypted plain text value
    """
    if not encrypted_value:
        return encrypted_value
    
    try:
        key = _get_encryption_key()
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_value.encode('utf-8'))
        return decrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise ValueError(f"Failed to decrypt value: {e}")


def encrypt_dict(data: dict) -> str:
    """
    Encrypt a dictionary (converts to JSON first)
    
    Args:
        data: Dictionary to encrypt
    
    Returns:
        Encrypted JSON string
    """
    import json
    json_str = json.dumps(data)
    return encrypt_value(json_str)


def decrypt_dict(encrypted_json: str) -> dict:
    """
    Decrypt an encrypted JSON string back to dictionary
    
    Args:
        encrypted_json: Encrypted JSON string
    
    Returns:
        Decrypted dictionary
    """
    import json
    decrypted = decrypt_value(encrypted_json)
    return json.loads(decrypted)
