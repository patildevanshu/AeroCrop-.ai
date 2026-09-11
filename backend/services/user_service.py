"""
AeroCrop.ai — User Management Service (MongoDB / Motor)

Handles registration, authentication verification, and profile management for farmers.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from database.models import User
from database.mongodb import get_next_sequence
from services.auth_service import AuthService

logger = logging.getLogger("aerocrop.users")


class UserService:
    """Service providing farmer user management operations using MongoDB."""

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
        db: AsyncIOMotorDatabase,
        full_name: str,
        password: str,
        district: str = "pune",
        phone_number: Optional[str] = None,
        email: Optional[str] = None,
        taluka_village: Optional[str] = None,
        preferred_language: str = "en",
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new farmer account in MongoDB.
        Returns (user, None) on success or (None, error_message) on failure.
        """
        phone_clean = UserService.normalize_phone(phone_number) if phone_number and phone_number.strip() else None
        email_clean = email.strip().lower() if email and email.strip() else None

        if not phone_clean and not email_clean:
            return None, "Either mobile phone number or email address is required."

        if len(password) < 6:
            return None, "Password must be at least 6 characters long."

        # Check for existing user with same phone or email
        or_conditions = []
        if phone_clean:
            or_conditions.append({"phone_number": phone_clean})
        if email_clean:
            or_conditions.append({"email": email_clean})

        existing = await db.users.find_one({"$or": or_conditions})
        if existing:
            if phone_clean and existing.get("phone_number") == phone_clean:
                return None, f"An account with phone number {phone_clean} is already registered."
            if email_clean and existing.get("email") == email_clean:
                return None, f"An account with email {email_clean} is already registered."

        # Generate atomic monotonic integer ID for user
        new_id = await get_next_sequence("user_id")
        hashed = AuthService.hash_password(password)
        now = datetime.now(timezone.utc)

        user_doc = {
            "id": new_id,
            "full_name": full_name.strip(),
            "phone_number": phone_clean,
            "email": email_clean,
            "hashed_password": hashed,
            "district": district.strip().lower(),
            "taluka_village": taluka_village.strip() if taluka_village else None,
            "preferred_language": preferred_language.strip().lower() if preferred_language in ("en", "mr", "hi") else "en",
            "token_version": 1,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }

        try:
            await db.users.insert_one(user_doc)
        except DuplicateKeyError:
            if phone_clean:
                return None, f"An account with phone number {phone_clean} is already registered."
            if email_clean:
                return None, f"An account with email {email_clean} is already registered."
            return None, "An account with these credentials is already registered."

        new_user = User(**user_doc)
        logger.info("[UserService] Registered new farmer: %s (ID: %d)", new_user.full_name, new_user.id)
        return new_user, None

    @staticmethod
    async def authenticate_user(
        db: AsyncIOMotorDatabase,
        identifier: str,
        password: str,
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Verify credentials and authenticate a user against MongoDB.
        Returns (user, None) on success or (None, error_message) on failure.
        """
        ident_clean = identifier.strip()
        phone_norm = UserService.normalize_phone(ident_clean)

        or_conditions = [
            {"email": ident_clean.lower()},
            {"phone_number": ident_clean},
        ]
        if phone_norm and phone_norm != ident_clean:
            or_conditions.append({"phone_number": phone_norm})

        doc = await db.users.find_one({"$or": or_conditions})
        if not doc:
            return None, "Invalid mobile number/email or password."

        user = User(**doc)
        if not AuthService.verify_password(password, user.hashed_password):
            return None, "Invalid mobile number/email or password."

        if not user.is_active:
            return None, "This farmer account is deactivated. Please contact support."

        return user, None

    @staticmethod
    async def update_profile(
        db: AsyncIOMotorDatabase,
        user: User,
        full_name: Optional[str] = None,
        district: Optional[str] = None,
        taluka_village: Optional[str] = None,
        preferred_language: Optional[str] = None,
    ) -> User:
        """Update farmer's profile preferences in MongoDB."""
        updates = {"updated_at": datetime.now(timezone.utc)}
        if full_name is not None and full_name.strip():
            user.full_name = full_name.strip()
            updates["full_name"] = user.full_name
        if district is not None and district.strip():
            user.district = district.strip().lower()
            updates["district"] = user.district
        if taluka_village is not None:
            user.taluka_village = taluka_village.strip() or None
            updates["taluka_village"] = user.taluka_village
        if preferred_language is not None and preferred_language.strip() in ("en", "mr", "hi"):
            user.preferred_language = preferred_language.strip()
            updates["preferred_language"] = user.preferred_language

        await db.users.update_one({"id": user.id}, {"$set": updates})
        return user

    @staticmethod
    async def change_password(
        db: AsyncIOMotorDatabase,
        user: User,
        current_password: str,
        new_password: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Change farmer password after verifying current password.
        Increments token_version to invalidate previous sessions.
        """
        if not AuthService.verify_password(current_password, user.hashed_password):
            return False, "Current password does not match."

        if len(new_password) < 6:
            return False, "New password must be at least 6 characters long."

        new_hashed = AuthService.hash_password(new_password)
        new_token_version = (user.token_version or 1) + 1

        await db.users.update_one(
            {"id": user.id},
            {
                "$set": {
                    "hashed_password": new_hashed,
                    "token_version": new_token_version,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )
        user.hashed_password = new_hashed
        user.token_version = new_token_version
        logger.info("[UserService] Password updated for farmer ID %d (session invalidated)", user.id)
        return True, None
