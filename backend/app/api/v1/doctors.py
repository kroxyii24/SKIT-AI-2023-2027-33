"""
Doctor onboarding flow:
  1. User registers a normal account, then applies with DoctorProfile (self-serve).
  2. Profile starts as is_verified_by_admin=False — invisible to patients, cannot
     be booked, cannot upload videos.
  3. An admin reviews medical_council_reg_no against the official registry
     (manual step in v1 — automation against the National Medical Register API
     is future scope) and flips is_verified_by_admin=True.
This gate is intentionally a hard blocker enforced at the API layer, not just
a UI hint, so an unverified doctor can never reach patients through any route.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.rbac import get_current_user, require_role, TokenPayload
from app.db.session import get_db
from app.models.domain import DoctorProfile, User, UserRole
from app.schemas.doctor import DoctorProfileCreate, DoctorProfileOut

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("/apply", response_model=DoctorProfileOut, status_code=201)
def apply_as_doctor(
    payload: DoctorProfileCreate,
    db: Session = Depends(get_db),
    user: TokenPayload = Depends(get_current_user),
):
    existing = db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == user.sub)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Doctor application already exists for this account")

    profile = DoctorProfile(user_id=user.sub, **payload.model_dump())
    db.add(profile)

    db_user = db.get(User, user.sub)
    db_user.role = UserRole.DOCTOR  # role changes immediately; verification gate is separate
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/", response_model=list[DoctorProfileOut])
def list_verified_doctors(specialization: str | None = None, db: Session = Depends(get_db)):
    """Public-facing list — only ever returns admin-verified doctors."""
    stmt = select(DoctorProfile).where(DoctorProfile.is_verified_by_admin.is_(True))
    if specialization:
        stmt = stmt.where(DoctorProfile.specialization == specialization)
    return db.execute(stmt).scalars().all()


@router.patch("/{doctor_id}/verify", response_model=DoctorProfileOut)
def verify_doctor(
    doctor_id: str,
    db: Session = Depends(get_db),
    _: TokenPayload = Depends(require_role("admin")),
):
    profile = db.get(DoctorProfile, doctor_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    profile.is_verified_by_admin = True
    db.commit()
    db.refresh(profile)
    return profile
