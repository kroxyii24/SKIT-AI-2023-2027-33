import uuid
from datetime import datetime
from pydantic import BaseModel, field_validator

from app.models.domain import ConsultationTier, AppointmentStatus


class AppointmentCreate(BaseModel):
    doctor_id: uuid.UUID
    scheduled_at: datetime
    consultation_tier: ConsultationTier
    notes: str | None = None

    @field_validator("scheduled_at")
    @classmethod
    def must_be_future(cls, v: datetime) -> datetime:
        if v <= datetime.now(v.tzinfo):
            raise ValueError("scheduled_at must be in the future")
        return v


class AppointmentOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    scheduled_at: str
    consultation_tier: ConsultationTier
    status: AppointmentStatus
    notes: str | None

    class Config:
        from_attributes = True


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus
