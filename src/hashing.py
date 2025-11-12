from passlib.context import CryptContext
import hashlib

# Create a single, reusable CryptContext instance
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bcrypt has a maximum password length of 72 bytes
MAX_PASSWORD_LENGTH = 72


def _prepare_password(password: str) -> str:
    """
    Prepare password for bcrypt hashing.
    If password is longer than 72 bytes, hash it first with SHA256.
    This ensures compatibility and security for long passwords.
    """
    password_bytes = password.encode('utf-8')
    
    # If password is longer than 72 bytes, pre-hash it with SHA256
    if len(password_bytes) > MAX_PASSWORD_LENGTH:
        # Use SHA256 to create a fixed-length hash, then encode as hex
        return hashlib.sha256(password_bytes).hexdigest()
    
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed one."""
    prepared_password = _prepare_password(plain_password)
    return pwd_context.verify(prepared_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashes a plain-text password."""
    prepared_password = _prepare_password(password)
    return pwd_context.hash(prepared_password)
