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
from services.otp_service import OtpService
try:
    from backend.services.email_logger import EmailAuditLogger
except ImportError:
    from services.email_logger import EmailAuditLogger
import backend.config as config

logger = logging.getLogger("aerocrop.controllers.auth")
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ── Schemas ──────────────────────────────────────────────────────────────────
class TestEmailRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=150, description="Target email address for deliverability testing")

class SendOtpRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=150, description="Farmer's email address")
    purpose: str = Field("register", description="Purpose: register | login | reset_password")


class VerifyOtpRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=150, description="Farmer's email address")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
    purpose: str = Field("register", description="Purpose: register | login | reset_password")


class RegisterWithOtpRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120, description="Farmer's full name")
    email: str = Field(..., min_length=5, max_length=150, description="Compulsory email address")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    district: str = Field(..., min_length=2, max_length=60, description="Farmer's compulsory Maharashtra district")
    phone_number: Optional[str] = Field(None, description="10-digit mobile number (optional)")
    taluka_village: Optional[str] = Field(None, description="Taluka or Village name")
    preferred_language: str = Field("en", description="Language code: en | mr | hi")


class LoginWithOtpRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=150, description="Farmer's email address")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120, description="Farmer's full name")
    email: str = Field(..., min_length=5, max_length=150, description="Compulsory email address")
    phone_number: Optional[str] = Field(None, description="10-digit mobile number")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    district: str = Field(..., min_length=2, max_length=60, description="Farmer's compulsory Maharashtra district")
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
@router.post("/send-otp", summary="Send email verification OTP")
async def send_otp(
    req: SendOtpRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Generate and email a 6-digit OTP to the farmer's email.
    Enforces a 60-second cooldown rate limit.
    """
    clean_email = req.email.strip().lower()
    if not clean_email or "@" not in clean_email or "." not in clean_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid email address.",
        )

    if req.purpose == "register":
        existing = await db.users.find_one({"email": clean_email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An account with email {clean_email} is already registered. Please sign in.",
            )
    elif req.purpose == "login":
        existing = await db.users.find_one({"email": clean_email})
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No account found with email {clean_email}. Please create an account first.",
            )

    success, msg = await OtpService.create_and_send_otp(db, clean_email, req.purpose)
    if not success:
        status_code = status.HTTP_429_TOO_MANY_REQUESTS if "wait" in msg.lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=msg)

    return {
        "status": "success",
        "message": msg,
        "cooldown_seconds": config.OTP_COOLDOWN_SECONDS,
    }


@router.get("/email-logs", summary="Get runtime email delivery logs and diagnostics")
async def get_email_logs(
    limit: int = 50,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Returns real-time email dispatch attempts, status, latency, and error details
    recorded in memory, MongoDB, and logs/email_runtime.log.
    """
    recent = EmailAuditLogger.get_recent_logs(limit=limit)
    db_logs = []
    if db is not None:
        try:
            cursor = db.email_logs.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
            db_logs = await cursor.to_list(length=limit)
        except Exception as exc:
            logger.debug("Could not query db email_logs: %s", exc)

    return {
        "status": "success",
        "log_file": config.EMAIL_RUNTIME_LOG_PATH,
        "smtp_server": f"{config.SMTP_HOST}:{config.SMTP_PORT}",
        "sender_email": config.SMTP_USER,
        "microservice_url": config.EMAIL_OTP_SERVICE_URL,
        "recent_in_memory_events": recent,
        "db_audit_records": db_logs,
        "runtime_log_tail": EmailAuditLogger.get_runtime_log_tail(max_lines=50),
    }


@router.post("/test-email", summary="Test dispatch an email to verify deliverability")
async def test_email(
    req: TestEmailRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Dispatches a test verification code to the specified email address
    and returns complete connection, handshake, and deliverability diagnostics.
    """
    clean_email = req.email.strip().lower()
    if not clean_email or "@" not in clean_email or "." not in clean_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")

    code = OtpService.generate_otp()
    success, msg, audit = await OtpService.dispatch_otp_email(clean_email, code, "test_deliverability")
    await EmailAuditLogger.record_to_mongodb(db, audit)

    return {
        "status": "success" if success else "failed",
        "message": msg,
        "audit": audit,
    }


@router.post("/verify-otp", summary="Verify email OTP code")
async def verify_otp(
    req: VerifyOtpRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Validate the 6-digit OTP code against the stored hash.
    Does not consume the OTP until registration or login completes.
    """
    clean_email = req.email.strip().lower()
    valid, err = await OtpService.verify_otp(db, clean_email, req.otp, req.purpose, mark_used=False)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    return {
        "status": "success",
        "message": "Verification code verified successfully.",
        "verified": True,
    }


@router.post("/register-with-otp", summary="Register farmer with verified email OTP")
async def register_with_otp(
    req: RegisterWithOtpRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Atomically verify the OTP and create a new farmer account.
    Returns access token and user metadata.
    """
    clean_email = req.email.strip().lower()
    valid, err = await OtpService.verify_otp(db, clean_email, req.otp, "register", mark_used=True)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    user, reg_err = await UserService.register_user(
        db=db,
        full_name=req.full_name,
        password=req.password,
        district=req.district,
        phone_number=req.phone_number,
        email=clean_email,
        taluka_village=req.taluka_village,
        preferred_language=req.preferred_language,
        is_verified=True,
    )

    if reg_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=reg_err)

    identifier = user.email or user.phone_number or str(user.id)
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


@router.post("/login-with-otp", summary="Passwordless login with email OTP")
async def login_with_otp(
    req: LoginWithOtpRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Authenticate farmer via verified 6-digit email OTP.
    Returns JWT access token.
    """
    clean_email = req.email.strip().lower()
    user_doc = await db.users.find_one({"email": clean_email})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account registered with this email address.",
        )

    user = User(**user_doc)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This farmer account is deactivated. Please contact support.",
        )

    valid, err = await OtpService.verify_otp(db, clean_email, req.otp, "login", mark_used=True)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    identifier = user.email or user.phone_number or str(user.id)
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
