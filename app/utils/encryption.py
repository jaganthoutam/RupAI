"""
Encryption and Security Utilities
Enterprise-grade encryption for sensitive data handling.
"""

import base64
import hashlib
import logging
import secrets
from typing import Any, Dict, Optional, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext

from app.config.settings import settings

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Enterprise encryption manager with multiple encryption methods.
    
    Features:
    - Symmetric encryption for data at rest
    - Password hashing with secure algorithms
    - Key derivation and management
    - Token generation for secure communications
    """
    
    def __init__(self):
        self.fernet: Optional[Fernet] = None
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=12
        )
        self.initialized = False
        
    async def initialize(self) -> None:
        """Initialize encryption systems."""
        try:
            logger.info("🔄 Initializing encryption manager...")
            
            # Initialize Fernet encryption
            key = self._derive_key_from_password(
                settings.ENCRYPTION_KEY,
                salt=b"mcp_payments_salt_2024"  # Static salt for consistency
            )
            self.fernet = Fernet(key)
            
            self.initialized = True
            logger.info("✅ Encryption manager initialized")
            
        except Exception as e:
            logger.error("❌ Failed to initialize encryption manager: %s", str(e))
            raise
    
    def _derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Derive Fernet-compatible key from password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # OWASP recommended minimum
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    # Data Encryption/Decryption
    def encrypt_data(self, data: Union[str, bytes, Dict[str, Any]]) -> str:
        """
        Encrypt sensitive data.
        
        Args:
            data: Data to encrypt (string, bytes, or dict)
            
        Returns:
            Base64-encoded encrypted data
        """
        if not self.initialized or not self.fernet:
            raise RuntimeError("Encryption manager not initialized")
        
        try:
            # Convert data to bytes
            if isinstance(data, dict):
                import json
                data_bytes = json.dumps(data).encode('utf-8')
            elif isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # Encrypt and encode
            encrypted = self.fernet.encrypt(data_bytes)
            return base64.urlsafe_b64encode(encrypted).decode('utf-8')
            
        except Exception as e:
            logger.error("Encryption error: %s", str(e))
            raise
    
    def decrypt_data(self, encrypted_data: str, return_type: str = "string") -> Union[str, bytes, Dict[str, Any]]:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            return_type: Type to return ("string", "bytes", "dict")
            
        Returns:
            Decrypted data in specified format
        """
        if not self.initialized or not self.fernet:
            raise RuntimeError("Encryption manager not initialized")
        
        try:
            # Decode and decrypt
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            
            # Return in requested format
            if return_type == "bytes":
                return decrypted_bytes
            elif return_type == "dict":
                import json
                return json.loads(decrypted_bytes.decode('utf-8'))
            else:  # string
                return decrypted_bytes.decode('utf-8')
                
        except Exception as e:
            logger.error("Decryption error: %s", str(e))
            raise
    
    # Password Hashing
    def hash_password(self, password: str) -> str:
        """
        Hash password with secure algorithm.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            logger.error("Password hashing error: %s", str(e))
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Previously hashed password
            
        Returns:
            True if password matches
        """
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error("Password verification error: %s", str(e))
            return False
    
    # Token Generation
    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate cryptographically secure random token.
        
        Args:
            length: Token length in bytes
            
        Returns:
            URL-safe base64-encoded token
        """
        try:
            token_bytes = secrets.token_bytes(length)
            return base64.urlsafe_b64encode(token_bytes).decode('utf-8')
        except Exception as e:
            logger.error("Token generation error: %s", str(e))
            raise
    
    def generate_api_key(self, prefix: str = "mcp") -> str:
        """
        Generate API key with prefix.
        
        Args:
            prefix: API key prefix
            
        Returns:
            Formatted API key
        """
        try:
            token = self.generate_secure_token(24)
            return f"{prefix}_{token}"
        except Exception as e:
            logger.error("API key generation error: %s", str(e))
            raise
    
    # Data Masking
    def mask_sensitive_data(self, data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
        """
        Mask sensitive data for logging/display.
        
        Args:
            data: Sensitive data to mask
            mask_char: Character to use for masking
            visible_chars: Number of characters to keep visible at start/end
            
        Returns:
            Masked data
        """
        if len(data) <= visible_chars * 2:
            return mask_char * len(data)
        
        start = data[:visible_chars]
        end = data[-visible_chars:]
        middle = mask_char * (len(data) - visible_chars * 2)
        
        return f"{start}{middle}{end}"
    
    # Hashing Utilities
    def hash_data(self, data: Union[str, bytes], algorithm: str = "sha256") -> str:
        """
        Hash data with specified algorithm.
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm ("sha256", "sha512", "md5")
            
        Returns:
            Hex-encoded hash
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if algorithm == "sha256":
                hash_obj = hashlib.sha256(data)
            elif algorithm == "sha512":
                hash_obj = hashlib.sha512(data)
            elif algorithm == "md5":
                hash_obj = hashlib.md5(data)
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            logger.error("Data hashing error: %s", str(e))
            raise
    
    def verify_data_integrity(self, data: Union[str, bytes], expected_hash: str, algorithm: str = "sha256") -> bool:
        """
        Verify data integrity using hash comparison.
        
        Args:
            data: Data to verify
            expected_hash: Expected hash value
            algorithm: Hash algorithm used
            
        Returns:
            True if data integrity is valid
        """
        try:
            actual_hash = self.hash_data(data, algorithm)
            return secrets.compare_digest(actual_hash, expected_hash)
        except Exception as e:
            logger.error("Data integrity verification error: %s", str(e))
            return False
    
    # PCI-DSS Compliance Helpers
    def encrypt_card_data(self, card_data: Dict[str, Any]) -> str:
        """
        Encrypt payment card data for PCI-DSS compliance.
        
        Args:
            card_data: Dictionary containing card information
            
        Returns:
            Encrypted card data token
        """
        # Remove or mask sensitive fields before encryption
        safe_data = {
            "last4": card_data.get("number", "")[-4:] if card_data.get("number") else "",
            "brand": card_data.get("brand", ""),
            "exp_month": card_data.get("exp_month", ""),
            "exp_year": card_data.get("exp_year", ""),
            "token": self.generate_secure_token(16)
        }
        
        return self.encrypt_data(safe_data)
    
    def mask_payment_data(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mask sensitive payment data for logging.
        
        Args:
            payment_data: Payment data dictionary
            
        Returns:
            Masked payment data
        """
        masked_data = payment_data.copy()
        
        # Mask sensitive fields
        if "card_number" in masked_data:
            masked_data["card_number"] = self.mask_sensitive_data(masked_data["card_number"])
        
        if "cvv" in masked_data:
            masked_data["cvv"] = "***"
        
        if "account_number" in masked_data:
            masked_data["account_number"] = self.mask_sensitive_data(masked_data["account_number"])
        
        if "routing_number" in masked_data:
            masked_data["routing_number"] = self.mask_sensitive_data(masked_data["routing_number"])
        
        return masked_data 