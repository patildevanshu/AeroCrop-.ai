"""
AeroCrop.ai — Authentication & Cryptography Service (MongoDB / Motor)

Provides:
  - Secure direct bcrypt password hashing & verification
  - JWT token issuance & claims validation with token_version invalidation
  - FastAPI authentication dependencies: get_current_user & get_optional_user
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

import config
from database.mongodb import get_db
from database.models import User

logger = logging.getLogger("aerocrop.auth")
security_scheme = HTTPBearer(auto_error=False)


class AuthService:
    """Security utility for direct bcrypt password hashing and JWT token management."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plaintext password using native bcrypt."""
        pw_bytes = password.encode("utf-8")[:72]
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(pw_bytes, salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against its bcrypt hash."""
        try:
            pw_bytes = plain_password.encode("utf-8")[:72]
            hash_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(pw_bytes, hash_bytes)
        except Exception as exc:
            logger.warning("[AuthService] Password verification failed with error: %s", exc)
            return False

    @staticmethod
    def create_access_token(user_id: int, phone_or_email: str, token_version: int = 1) -> str:
        """Generate a signed JWT access token with token version claim."""
        expire = datetime.now(timezone.utc) + timedelta(days=config.JWT_ACCESS_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": str(user_id),
            "identifier": phone_or_email,
            "tv": token_version,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
        token = jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
        return token

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """Decode and validate a JWT access token."""
        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM],
            )
            return payload
        except jwt.PyJWTError as exc:
            logger.debug("[AuthService] Invalid token: %s", exc)
            return None

    @staticmethod
    async def revoke_all_user_tokens(db: AsyncIOMotorDatabase, user: User) -> None:
        """Increment token_version to invalidate all existing JWT tokens for this user."""
        new_version = (user.token_version or 1) + 1
        user.token_version = new_version
        await db.users.update_one(
            {"id": user.id},
            {"$set": {"token_version": new_version, "updated_at": datetime.now(timezone.utc)}},
        )
        logger.info("[AuthService] Revoked tokens for user #%d (new token_version: %d)", user.id, user.token_version)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> User:
    """
    FastAPI dependency requiring an authenticated user.
    Raises 401 if missing, invalid, expired, or revoked via token_version.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = AuthService.decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identity in token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    doc = await db.users.find_one({"id": user_id, "is_active": True})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or disabled.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = User(**doc)

    # Check token version to detect revoked/logged-out sessions
    token_ver = payload.get("tv")
    if token_ver is not None and token_ver != getattr(user, "token_version", 1):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or was revoked. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Optional[User]:
    """
    FastAPI dependency for endpoints supporting both authenticated users and guests.
    Returns User if valid token is supplied, otherwise returns None without error.
    """
    if not credentials or not credentials.credentials:
        return None

    payload = AuthService.decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None

    try:
        user_id = int(payload["sub"])
        doc = await db.users.find_one({"id": user_id, "is_active": True})
        if not doc:
            return None

        user = User(**doc)
        token_ver = payload.get("tv")
        if token_ver is not None and token_ver != getattr(user, "token_version", 1):
            return None

        return user
    except Exception:
        return None
