"""Password hashing and verification using bcrypt (via passlib).

Wraps the passlib ``CryptContext`` with a convenient API.
"""

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return a bcrypt hash of the given plain-text password."""
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its bcrypt hash.

    Uses constant-time comparison to prevent timing attacks.
    """
    return _pwd_context.verify(plain_password, hashed_password)
