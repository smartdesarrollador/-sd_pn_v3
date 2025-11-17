"""
Authentication Manager
Manages password hashing, verification, and account locking
"""
import hashlib
import secrets
import time
from pathlib import Path
from typing import Optional, Tuple
from dotenv import load_dotenv, set_key, find_dotenv
import os


class AuthManager:
    """Manages authentication, password hashing, and account security"""

    # Constants
    MAX_ATTEMPTS = 5  # Maximum failed login attempts
    LOCK_DURATION = 300  # Lock duration in seconds (5 minutes)

    def __init__(self, env_file: str = ".env"):
        """
        Initialize AuthManager

        Args:
            env_file: Path to .env file (default: ".env")
        """
        self.env_file = Path(env_file)

        # Ensure .env file exists
        if not self.env_file.exists():
            self.env_file.touch()

        # Load environment variables
        load_dotenv(self.env_file)

    def _get_env(self, key: str, default: str = "") -> str:
        """Get environment variable value"""
        return os.getenv(key, default)

    def _set_env(self, key: str, value: str):
        """Set environment variable value in .env file"""
        env_path = str(self.env_file)
        set_key(env_path, key, value)
        # Update os.environ immediately
        os.environ[key] = value

    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hash password with SHA256 + salt

        Args:
            password: Plain text password
            salt: Optional salt (generates random if None)

        Returns:
            Tuple of (password_hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(32)  # 64 characters

        # Combine password + salt
        salted = password + salt

        # Hash with SHA256
        hash_obj = hashlib.sha256(salted.encode())
        password_hash = hash_obj.hexdigest()

        return password_hash, salt

    def verify_password(self, password: str) -> bool:
        """
        Verify password against stored hash

        Args:
            password: Plain text password to verify

        Returns:
            True if password is correct, False otherwise
        """
        stored_hash = self._get_env("PASSWORD_HASH")
        stored_salt = self._get_env("PASSWORD_SALT")

        if not stored_hash or not stored_salt:
            return False

        # Hash the provided password with stored salt
        new_hash, _ = self.hash_password(password, stored_salt)

        return new_hash == stored_hash

    def is_first_time(self) -> bool:
        """
        Check if this is the first time running (no password set)

        Returns:
            True if no password hash exists, False otherwise
        """
        password_hash = self._get_env("PASSWORD_HASH")
        return not password_hash

    def set_password(self, password: str):
        """
        Set new password (hash and save to .env)

        Args:
            password: Plain text password
        """
        password_hash, salt = self.hash_password(password)

        # Save to .env
        self._set_env("PASSWORD_HASH", password_hash)
        self._set_env("PASSWORD_SALT", salt)

        # Reset failed attempts
        self.reset_failed_attempts()

    def change_password(self, old_password: str, new_password: str) -> bool:
        """
        Change password (verify old password first)

        Args:
            old_password: Current password
            new_password: New password

        Returns:
            True if password changed successfully, False if old password incorrect
        """
        # Verify old password
        if not self.verify_password(old_password):
            return False

        # Set new password
        self.set_password(new_password)
        return True

    def get_failed_attempts(self) -> int:
        """
        Get number of failed login attempts

        Returns:
            Number of failed attempts
        """
        attempts_str = self._get_env("FAILED_ATTEMPTS", "0")
        try:
            return int(attempts_str)
        except ValueError:
            return 0

    def increment_failed_attempts(self):
        """Increment failed login attempts counter"""
        current = self.get_failed_attempts()
        self._set_env("FAILED_ATTEMPTS", str(current + 1))

        # Check if should lock account
        if current + 1 >= self.MAX_ATTEMPTS:
            self.lock_account(self.LOCK_DURATION)

    def reset_failed_attempts(self):
        """Reset failed login attempts counter to 0"""
        self._set_env("FAILED_ATTEMPTS", "0")
        # Also clear lock timestamp
        self._set_env("LOCK_TIMESTAMP", "0")

    def is_locked(self) -> bool:
        """
        Check if account is currently locked

        Returns:
            True if account is locked, False otherwise
        """
        lock_timestamp_str = self._get_env("LOCK_TIMESTAMP", "0")
        try:
            lock_timestamp = int(lock_timestamp_str)
        except ValueError:
            return False

        if lock_timestamp == 0:
            return False

        current_time = int(time.time())

        # Check if lock has expired
        if current_time >= lock_timestamp:
            # Lock expired, reset
            self.reset_failed_attempts()
            return False

        return True

    def get_lock_time_remaining(self) -> int:
        """
        Get remaining lock time in seconds

        Returns:
            Seconds remaining (0 if not locked)
        """
        if not self.is_locked():
            return 0

        lock_timestamp_str = self._get_env("LOCK_TIMESTAMP", "0")
        try:
            lock_timestamp = int(lock_timestamp_str)
        except ValueError:
            return 0

        current_time = int(time.time())
        remaining = lock_timestamp - current_time

        return max(0, remaining)

    def lock_account(self, duration: int):
        """
        Lock account for specified duration

        Args:
            duration: Lock duration in seconds
        """
        lock_until = int(time.time()) + duration
        self._set_env("LOCK_TIMESTAMP", str(lock_until))
