"""
Video library: verified doctors upload, admin moderates before public visibility.
Moderation gate (is_approved) is separate from doctor verification — a
verified doctor's individual video can still be rejected (e.g. off-topic,
poor quality, or borderline medical claims), so both flags matter.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.rbac import get_current_user, require_role, TokenPayload
from app.core.audit import log_action
from app.db.session import get_db
from app.models.domain import EducationalVideo, DoctorProfile
from app.schemas.video import VideoUploadRequest, VideoOut

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/", response_model=VideoOut, status_code=201)
def upload_video(
    payload: VideoUploadRequest,
    db: Session = Depends(get_db),
    user: TokenPayload = Depends(require_role("doctor")),
):
    doctor_profile = db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == user.sub)
    ).scalar_one_or_none()
    if not doctor_profile or not doctor_profile.is_verified_by_admin:
        raise HTTPException(status_code=403, detail="Only admin-verified doctors can upload videos")

    video = EducationalVideo(doctor_id=doctor_profile.id, **payload.model_dump())
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


@router.get("/", response_model=list[VideoOut])
def list_videos(category: str | None = None, language: str | None = None, db: Session = Depends(get_db)):
    """Public endpoint — only ever returns admin-approved videos."""
    stmt = select(EducationalVideo).where(EducationalVideo.is_approved.is_(True))
    if category:
        stmt = stmt.where(EducationalVideo.category == category)
    if language:
        stmt = stmt.where(EducationalVideo.language == language)
    return db.execute(stmt).scalars().all()


@router.patch("/{video_id}/approve", response_model=VideoOut)
def approve_video(video_id: str, db: Session = Depends(get_db), admin: TokenPayload = Depends(require_role("admin"))):
    video = db.get(EducationalVideo, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    video.is_approved = True
    log_action(db, action="video.approve", actor_user_id=admin.sub, target_type="educational_video", target_id=video_id)
    db.commit()
    db.refresh(video)
    return video


@router.post("/{video_id}/view")
def increment_view_count(video_id: str, db: Session = Depends(get_db)):
    result = db.execute(
        update(EducationalVideo)
        .where(EducationalVideo.id == video_id, EducationalVideo.is_approved.is_(True))
        .values(view_count=EducationalVideo.view_count + 1)
    )
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"status": "ok"}
