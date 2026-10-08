import json

import redis
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.core.rate_limit import limiter
from app.core.config import settings
from app.db.session import get_db
from app.models.domain import User, UserRole
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    VerifyOTPRequest,
    ResendOTPRequest,
    OTPResponse,
)
from app.services.auth.otp import generate_otp, hash_otp, send_otp_email


router = APIRouter(prefix="/auth", tags=["auth"])


redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


def get_otp_key(email: str) -> str:
    return f"registration_otp:{email.lower()}"


@router.post(
    "/register/request-otp",
    response_model=OTPResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("5/hour")
def request_registration_otp(
    request: Request,
    payload: UserRegister,
    db: Session = Depends(get_db),
):
    email = str(payload.email).lower()

    # Check whether phone is already registered
    existing_phone = db.execute(
        select(User).where(
            User.phone_number == payload.phone_number
        )
    ).scalar_one_or_none()

    if existing_phone:
        raise HTTPException(
            status_code=400,
            detail="Phone number already registered",
        )

    # Check whether email is already registered
    existing_email = db.execute(
        select(User).where(
            User.email == email
        )
    ).scalar_one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    otp = generate_otp()

    pending_registration = {
        "full_name": payload.full_name,
        "phone_number": payload.phone_number,
        "email": email,
        "hashed_password": hash_password(payload.password),
        "preferred_language": payload.preferred_language or "en",
        "otp_hash": hash_otp(otp),
        "attempts": 0,
    }

    redis_client.setex(
        get_otp_key(email),
        settings.OTP_EXPIRE_SECONDS,
        json.dumps(pending_registration),
    )

    try:
        send_otp_email(email, otp)
    except Exception:
        redis_client.delete(get_otp_key(email))

        raise HTTPException(
            status_code=500,
            detail="Unable to send verification email. Please try again.",
        )

    return OTPResponse(
        message="Verification OTP sent successfully.",
    )


@router.post(
    "/register/resend-otp",
    response_model=OTPResponse,
)
@limiter.limit("3/10minutes")
def resend_registration_otp(
    request: Request,
    payload: ResendOTPRequest,
):
    email = str(payload.email).lower()

    key = get_otp_key(email)
    stored = redis_client.get(key)

    if not stored:
        raise HTTPException(
            status_code=400,
            detail="Registration session expired. Please register again.",
        )

    pending_registration = json.loads(stored)

    otp = generate_otp()

    pending_registration["otp_hash"] = hash_otp(otp)
    pending_registration["attempts"] = 0

    redis_client.setex(
        key,
        settings.OTP_EXPIRE_SECONDS,
        json.dumps(pending_registration),
    )

    try:
        send_otp_email(email, otp)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to resend verification email.",
        )

    return OTPResponse(
        message="A new verification OTP has been sent.",
    )


@router.post(
    "/register/verify-otp",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/10minutes")
def verify_registration_otp(
    request: Request,
    payload: VerifyOTPRequest,
    db: Session = Depends(get_db),
):
    email = str(payload.email).lower()

    key = get_otp_key(email)
    stored = redis_client.get(key)

    if not stored:
        raise HTTPException(
            status_code=400,
            detail="OTP expired or registration session not found.",
        )

    pending_registration = json.loads(stored)

    attempts = int(pending_registration.get("attempts", 0))

    if attempts >= settings.OTP_MAX_ATTEMPTS:
        redis_client.delete(key)

        raise HTTPException(
            status_code=429,
            detail="Too many incorrect OTP attempts. Please register again.",
        )

    if hash_otp(payload.otp) != pending_registration["otp_hash"]:
        pending_registration["attempts"] = attempts + 1

        redis_client.setex(
            key,
            settings.OTP_EXPIRE_SECONDS,
            json.dumps(pending_registration),
        )

        remaining = settings.OTP_MAX_ATTEMPTS - attempts - 1

        raise HTTPException(
            status_code=400,
            detail=f"Invalid OTP. {remaining} attempts remaining.",
        )

    # Final duplicate checks before creating the user
    existing_phone = db.execute(
        select(User).where(
            User.phone_number == pending_registration["phone_number"]
        )
    ).scalar_one_or_none()

    if existing_phone:
        redis_client.delete(key)

        raise HTTPException(
            status_code=400,
            detail="Phone number already registered.",
        )

    existing_email = db.execute(
        select(User).where(
            User.email == email
        )
    ).scalar_one_or_none()

    if existing_email:
        redis_client.delete(key)

        raise HTTPException(
            status_code=400,
            detail="Email already registered.",
        )

    user = User(
        full_name=pending_registration["full_name"],
        phone_number=pending_registration["phone_number"],
        email=email,
        hashed_password=pending_registration["hashed_password"],
        role=UserRole.CITIZEN,
        preferred_language=pending_registration["preferred_language"],
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # OTP/session can no longer be reused
    redis_client.delete(key)

    return TokenResponse(
        access_token=create_access_token(
            str(user.id),
            user.role.value,
        ),
        refresh_token=create_refresh_token(
            str(user.id),
        ),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
@limiter.limit("10/minute")
def login(
    request: Request,
    payload: UserLogin,
    db: Session = Depends(get_db),
):
    user = db.execute(
        select(User).where(
            User.phone_number == payload.phone_number
        )
    ).scalar_one_or_none()

    if not user or not verify_password(
        payload.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid phone number or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account is deactivated",
        )

    return TokenResponse(
        access_token=create_access_token(
            str(user.id),
            user.role.value,
        ),
        refresh_token=create_refresh_token(
            str(user.id),
        ),
    )