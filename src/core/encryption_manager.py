"""
Encryption Manager
Maneja el cifrado y descifrado de datos sensibles usando AES-256 (Fernet)
"""

import os
import logging
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv, set_key

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Gestor de cifrado para datos sensibles
    Utiliza Fernet (AES-256) para cifrar/descifrar contraseñas
    """

    def __init__(self, env_file: str = ".env"):
        """
        Initialize encryption manager

        Args:
            env_file: Path to .env file
        """
        self.env_file = Path(env_file)
        self.cipher_suite: Optional[Fernet] = None
        self._initialize()

    def _initialize(self):
        """Initialize encryption key from .env or create new one"""
        # Load .env file
        load_dotenv(self.env_file)

        # Get or create encryption key
        encryption_key = os.getenv("ENCRYPTION_KEY")

        if not encryption_key:
            # Generate new key if doesn't exist
            logger.info("No encryption key found. Generating new key...")
            encryption_key = self._generate_key()
            self._save_key_to_env(encryption_key)
            logger.info("New encryption key generated and saved to .env")

        # Initialize cipher suite
        try:
            self.cipher_suite = Fernet(encryption_key.encode())
            logger.info("Encryption manager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing encryption: {e}")
            raise

    def _generate_key(self) -> str:
        """
        Generate a new Fernet encryption key

        Returns:
            str: Base64-encoded encryption key
        """
        key = Fernet.generate_key()
        return key.decode()

    def _save_key_to_env(self, key: str):
        """
        Save encryption key to .env file

        Args:
            key: Encryption key to save
        """
        # Create .env if doesn't exist
        if not self.env_file.exists():
            self.env_file.touch()
            # Set restrictive permissions (only owner can read/write)
            if os.name != 'nt':  # Unix-like systems
                os.chmod(self.env_file, 0o600)

        # Save key to .env
        set_key(self.env_file, "ENCRYPTION_KEY", key)

        # Add .env to .gitignore if not already there
        self._add_to_gitignore()

    def _add_to_gitignore(self):
        """Add .env to .gitignore to prevent committing secrets"""
        gitignore = Path(".gitignore")

        if gitignore.exists():
            with open(gitignore, "r", encoding="utf-8") as f:
                content = f.read()

            if ".env" not in content:
                with open(gitignore, "a", encoding="utf-8") as f:
                    f.write("\n# Environment variables (contains encryption key)\n")
                    f.write(".env\n")
                logger.info("Added .env to .gitignore")

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string

        Args:
            plaintext: Text to encrypt

        Returns:
            str: Encrypted text (base64-encoded)
        """
        if not plaintext:
            return ""

        if not self.cipher_suite:
            raise RuntimeError("Encryption manager not initialized")

        try:
            encrypted_bytes = self.cipher_suite.encrypt(plaintext.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise

    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt encrypted text

        Args:
            encrypted_text: Encrypted text (base64-encoded)

        Returns:
            str: Decrypted plaintext
        """
        if not encrypted_text:
            return ""

        if not self.cipher_suite:
            raise RuntimeError("Encryption manager not initialized")

        try:
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_text.encode())
            return decrypted_bytes.decode()
        except InvalidToken:
            logger.error("Invalid token - decryption failed (wrong key or corrupted data)")
            raise ValueError("Failed to decrypt: Invalid encryption key")
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise

    def is_encrypted(self, text: str) -> bool:
        """
        Check if text appears to be encrypted

        Args:
            text: Text to check

        Returns:
            bool: True if text appears encrypted
        """
        try:
            # Try to decode as base64 and check if it's Fernet format
            if not text:
                return False

            # Fernet tokens start with "gAAAAA" after base64 encoding
            return text.startswith("gAAAAA")
        except Exception:
            return False

    def verify_key_integrity(self) -> bool:
        """
        Verify encryption key is valid

        Returns:
            bool: True if key is valid and working
        """
        try:
            test_data = "test_encryption_integrity"
            encrypted = self.encrypt(test_data)
            decrypted = self.decrypt(encrypted)
            return test_data == decrypted
        except Exception:
            return False
