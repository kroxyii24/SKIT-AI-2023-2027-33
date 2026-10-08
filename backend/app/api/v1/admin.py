"""
Admin analytics — read-only aggregate endpoints. Deliberately returns only
aggregates/counts, never raw per-user rows, even to admins, on this endpoint —
detailed per-record lookups go through the specific resource endpoints
(which have their own RBAC + audit logging), keeping this dashboard's blast
radius small if the endpoint itself were ever misused.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.rbac import require_role, TokenPayload
from app.db.session import get_db
from app.models.domain import User, DoctorProfile, EducationalVideo, Appointment, ChatMessage

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def dashboard_stats(db: Session = Depends(get_db), _: TokenPayload = Depends(require_role("admin"))):
    total_users = db.execute(select(func.count(User.id))).scalar()
    total_doctors_verified = db.execute(
        select(func.count(DoctorProfile.id)).where(DoctorProfile.is_verified_by_admin.is_(True))
    ).scalar()
    total_doctors_pending = db.execute(
        select(func.count(DoctorProfile.id)).where(DoctorProfile.is_verified_by_admin.is_(False))
    ).scalar()
    videos_pending_approval = db.execute(
        select(func.count(EducationalVideo.id)).where(EducationalVideo.is_approved.is_(False))
    ).scalar()
    total_appointments = db.execute(select(func.count(Appointment.id))).scalar()
    total_emergency_flags = db.execute(
        select(func.count(ChatMessage.id)).where(ChatMessage.was_emergency_flagged.is_(True))
    ).scalar()

    return {
        "total_users": total_users,
        "verified_doctors": total_doctors_verified,
        "pending_doctor_verifications": total_doctors_pending,
        "videos_pending_approval": videos_pending_approval,
        "total_appointments": total_appointments,
        "emergency_flags_triggered": total_emergency_flags,
    }


@router.get("/doctors/pending")
def pending_doctor_applications(db: Session = Depends(get_db), _: TokenPayload = Depends(require_role("admin"))):
    stmt = select(DoctorProfile).where(DoctorProfile.is_verified_by_admin.is_(False))
    return db.execute(stmt).scalars().all()


@router.get("/videos/pending")
def pending_videos(db: Session = Depends(get_db), _: TokenPayload = Depends(require_role("admin"))):
    stmt = select(EducationalVideo).where(EducationalVideo.is_approved.is_(False))
    return db.execute(stmt).scalars().all()
