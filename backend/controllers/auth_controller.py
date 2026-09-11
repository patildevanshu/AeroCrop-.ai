"""
AeroCrop.ai — Farmer Authentication Controller

Endpoints:
  POST /api/auth/register → Register a new farmer account
  POST /api/auth/login    → Login with phone number/email and password
  GET  /api/auth/me       → Get currently authenticated farmer's profile
  PUT  /api/auth/profile  → Update profile details (district, name, language)
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase

from database.mongodb import get_db
from database.models import User
from services.auth_service import AuthService, get_current_user
from services.user_service import UserService

logger = logging.getLogger("aerocrop.controllers.auth")
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ── Schemas ──────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120, description="Farmer's full name")
    phone_number: Optional[str] = Field(None, description="10-digit mobile number")
    email: Optional[str] = Field(None, description="Email address (optional)")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    district: str = Field("pune", description="Default Maharashtra district")
    taluka_village: Optional[str] = Field(None, description="Taluka or Village name")
    preferred_language: str = Field("en", description="Language code: en | mr | hi")


class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Registered mobile number or email")
    password: str = Field(..., description="Password")


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    district: Optional[str] = None
    taluka_village: Optional[str] = None
    preferred_language: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., description="Farmer's current password")
    new_password: str = Field(..., min_length=6, description="New password (min 6 characters)")


# ── Endpoints ────────────────────────────────────────────────────────────────
@router.post("/register", summary="Register a new farmer account")
async def register(
    req: RegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Register a farmer with either mobile number or email.
    Returns access token and user metadata.
    """
    user, err = await UserService.register_user(
        db=db,
        full_name=req.full_name,
        password=req.password,
        district=req.district,
        phone_number=req.phone_number,
        email=req.email,
        taluka_village=req.taluka_village,
        preferred_language=req.preferred_language,
    )

    if err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    identifier = user.phone_number or user.email or str(user.id)
    token = AuthService.create_access_token(user.id, identifier, getattr(user, "token_version", 1))

    return {
        "status": "success",
        "message": f"Welcome to AeroCrop.ai, {user.full_name}!",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "district": user.district,
            "taluka_village": user.taluka_village,
            "preferred_language": user.preferred_language,
        },
    }


@router.post("/login", summary="Farmer login")
async def login(
    req: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Authenticate with phone number or email and password.
    Returns JWT access token.
    """
    user, err = await UserService.authenticate_user(
        db=db,
        identifier=req.identifier,
        password=req.password,
    )

    if err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=err)

    identifier = user.phone_number or user.email or str(user.id)
    token = AuthService.create_access_token(user.id, identifier, getattr(user, "token_version", 1))

    return {
        "status": "success",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "district": user.district,
            "taluka_village": user.taluka_village,
            "preferred_language": user.preferred_language,
        },
    }


@router.post("/logout", summary="Remote logout & token invalidation")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Invalidates all currently active JWT tokens for this user by incrementing token_version.
    """
    await AuthService.revoke_all_user_tokens(db, current_user)
    return {
        "status": "success",
        "message": "Successfully logged out. All existing sessions have been invalidated.",
    }


@router.get("/me", summary="Get current farmer profile")
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Returns profile information for the authenticated farmer."""
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "phone_number": current_user.phone_number,
        "email": current_user.email,
        "district": current_user.district,
        "taluka_village": current_user.taluka_village,
        "preferred_language": current_user.preferred_language,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }


@router.put("/profile", summary="Update farmer profile")
async def update_profile(
    req: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Update farmer profile settings."""
    user = await UserService.update_profile(
        db=db,
        user=current_user,
        full_name=req.full_name,
        district=req.district,
        taluka_village=req.taluka_village,
        preferred_language=req.preferred_language,
    )
    return {
        "status": "success",
        "message": "Profile updated successfully.",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "district": user.district,
            "taluka_village": user.taluka_village,
            "preferred_language": user.preferred_language,
        },
    }


@router.put("/change-password", summary="Change farmer password")
async def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Change account password.
    Requires current password verification and issues a new access token.
    """
    success, err = await UserService.change_password(
        db=db,
        user=current_user,
        current_password=req.current_password,
        new_password=req.new_password,
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    identifier = current_user.phone_number or current_user.email or str(current_user.id)
    new_token = AuthService.create_access_token(
        current_user.id, identifier, getattr(current_user, "token_version", 1)
    )

    return {
        "status": "success",
        "message": "Password changed successfully.",
        "access_token": new_token,
        "token_type": "bearer",
    }
