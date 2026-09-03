"""
AeroCrop.ai — User Management Service

Handles registration, authentication verification, and profile management for farmers.
"""

import logging
from typing import Optional, Tuple

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from services.auth_service import AuthService

logger = logging.getLogger("aerocrop.users")


class UserService:
    """Service providing farmer user management operations."""

    @staticmethod
    def normalize_phone(phone: Optional[str]) -> Optional[str]:
        """Normalize a phone number to standard digits, stripping spaces, +91, and leading zeros."""
        if not phone:
            return None
        raw = phone.strip()
        if raw.startswith("+91"):
            raw = raw[3:].strip()
        elif raw.startswith("+"):
            raw = raw[1:].strip()
        cleaned = "".join(c for c in raw if c.isdigit())
        if len(cleaned) == 12 and cleaned.startswith("91"):
            cleaned = cleaned[2:]
        elif len(cleaned) == 11 and cleaned.startswith("0"):
            cleaned = cleaned[1:]
        return cleaned if cleaned else None

    @staticmethod
    async def register_user(
        db: AsyncSession,
        full_name: str,
        password: str,
        district: str = "pune",
        phone_number: Optional[str] = None,
        email: Optional[str] = None,
        taluka_village: Optional[str] = None,
        preferred_language: str = "en",
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new farmer account.
        Returns (user, None) on success or (None, error_message) on failure.
        """
        # Validate that at least phone or email is provided
        phone_clean = UserService.normalize_phone(phone_number) if phone_number and phone_number.strip() else None
        email_clean = email.strip().lower() if email and email.strip() else None

        if not phone_clean and not email_clean:
            return None, "Either mobile phone number or email address is required."

        if len(password) < 6:
            return None, "Password must be at least 6 characters long."

        # Check for existing user with same phone or email
        conditions = []
        if phone_clean:
            conditions.append(User.phone_number == phone_clean)
        if email_clean:
            conditions.append(User.email == email_clean)

        existing_res = await db.execute(select(User).where(or_(*conditions)))
        existing = existing_res.scalar_one_or_none()

        if existing:
            if phone_clean and existing.phone_number == phone_clean:
                return None, f"An account with phone number {phone_clean} is already registered."
            if email_clean and existing.email == email_clean:
                return None, f"An account with email {email_clean} is already registered."

        # Create new user
        hashed = AuthService.hash_password(password)
        new_user = User(
            full_name=full_name.strip(),
            phone_number=phone_clean,
            email=email_clean,
            hashed_password=hashed,
            district=district.strip().lower(),
            taluka_village=taluka_village.strip() if taluka_village else None,
            preferred_language=preferred_language.strip().lower() if preferred_language in ("en", "mr", "hi") else "en",
        )
        db.add(new_user)
        await db.flush()
        await db.refresh(new_user)
        logger.info("[UserService] Registered new farmer: %s (ID: %d)", new_user.full_name, new_user.id)
        return new_user, None

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        identifier: str,  # Phone number or email
        password: str,
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Verify credentials and authenticate a user.
        Returns (user, None) on success or (None, error_message) on failure.
        """
        ident_clean = identifier.strip()
        phone_norm = UserService.normalize_phone(ident_clean)

        conditions = [
            User.email == ident_clean.lower(),
            User.phone_number == ident_clean,
        ]
        if phone_norm and phone_norm != ident_clean:
            conditions.append(User.phone_number == phone_norm)

        query = select(User).where(or_(*conditions))
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            return None, "Invalid mobile number/email or password."

        if not AuthService.verify_password(password, user.hashed_password):
            return None, "Invalid mobile number/email or password."

        if not user.is_active:
            return None, "This farmer account is deactivated. Please contact support."

        return user, None

    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user: User,
        full_name: Optional[str] = None,
        district: Optional[str] = None,
        taluka_village: Optional[str] = None,
        preferred_language: Optional[str] = None,
    ) -> User:
        """Update farmer's profile preferences."""
        if full_name is not None and full_name.strip():
            user.full_name = full_name.strip()
        if district is not None and district.strip():
            user.district = district.strip().lower()
        if taluka_village is not None:
            user.taluka_village = taluka_village.strip() or None
        if preferred_language is not None and preferred_language.strip() in ("en", "mr", "hi"):
            user.preferred_language = preferred_language.strip()

        await db.flush()
        await db.refresh(user)
        return user
