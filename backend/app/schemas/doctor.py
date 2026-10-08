import uuid
from pydantic import BaseModel, Field

from app.models.domain import ConsultationTier


class DoctorProfileCreate(BaseModel):
    medical_council_reg_no: str = Field(min_length=3, max_length=50)
    specialization: str
    years_experience: int = Field(ge=0, le=70)
    bio: str | None = None
    default_consultation_tier: ConsultationTier = ConsultationTier.FREE


class DoctorProfileOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    specialization: str
    years_experience: int
    bio: str | None
    is_verified_by_admin: bool
    default_consultation_tier: ConsultationTier
    average_rating: float

    class Config:
        from_attributes = True
