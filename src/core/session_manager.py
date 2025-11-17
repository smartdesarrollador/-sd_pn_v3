"""
Session Manager
Manages user sessions with tokens and expiration
"""
import secrets
import time
from pathlib import Path
from dotenv import load_dotenv, set_key, find_dotenv
import os


class SessionManager:
    """Manages user sessions with secure tokens"""

    # Session durations in hours
    SESSION_DURATION_NORMAL = 1  # 1 hours
    SESSION_DURATION_REMEMBER = 24  # 24 hours

    def __init__(self, env_file: str = ".env"):
        """
        Initialize SessionManager

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

    def create_session(self, remember: bool = False) -> str:
        """
        Create new session with token

        Args:
            remember: If True, session lasts 24 hours; otherwise 8 hours

        Returns:
            Session token (random 64-character string)
        """
        # Generate secure random token
        token = secrets.token_urlsafe(48)  # ~64 characters

        # Calculate expiration time
        duration_hours = self.SESSION_DURATION_REMEMBER if remember else self.SESSION_DURATION_NORMAL
        expires = int(time.time()) + (duration_hours * 3600)

        # Save to .env
        self._set_env("SESSION_TOKEN", token)
        self._set_env("SESSION_EXPIRES", str(expires))

        return token

    def validate_session(self) -> bool:
        """
        Validate current session

        Returns:
            True if session is valid and not expired, False otherwise
        """
        token = self._get_env("SESSION_TOKEN")
        expires_str = self._get_env("SESSION_EXPIRES", "0")

        # No token = no session
        if not token:
            return False

        # Parse expiration timestamp
        try:
            expires = int(expires_str)
        except ValueError:
            return False

        # Check if expired
        current_time = int(time.time())
        if current_time > expires:
            # Session expired, clean up
            self.invalidate_session()
            return False

        return True

    def get_session_token(self) -> str:
        """
        Get current session token

        Returns:
            Session token or empty string if no session
        """
        return self._get_env("SESSION_TOKEN", "")

    def invalidate_session(self):
        """Invalidate (delete) current session"""
        self._set_env("SESSION_TOKEN", "")
        self._set_env("SESSION_EXPIRES", "0")

    def is_session_expired(self) -> bool:
        """
        Check if session is expired (without invalidating it)

        Returns:
            True if session exists and is expired, False otherwise
        """
        token = self._get_env("SESSION_TOKEN")
        expires_str = self._get_env("SESSION_EXPIRES", "0")

        # No token = not expired (no session)
        if not token:
            return False

        # Parse expiration timestamp
        try:
            expires = int(expires_str)
        except ValueError:
            return False

        # Check if expired
        current_time = int(time.time())
        return current_time > expires

    def get_session_time_remaining(self) -> int:
        """
        Get remaining session time in seconds

        Returns:
            Seconds remaining (0 if expired or no session)
        """
        if not self.validate_session():
            return 0

        expires_str = self._get_env("SESSION_EXPIRES", "0")
        try:
            expires = int(expires_str)
        except ValueError:
            return 0

        current_time = int(time.time())
        remaining = expires - current_time

        return max(0, remaining)

    def extend_session(self, hours: int = 8):
        """
        Extend current session by specified hours

        Args:
            hours: Hours to extend session (default: 8)
        """
        if not self.validate_session():
            return

        # Calculate new expiration
        new_expires = int(time.time()) + (hours * 3600)
        self._set_env("SESSION_EXPIRES", str(new_expires))
