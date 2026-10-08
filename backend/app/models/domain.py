
"""
Core domain models for JanSwasthya AI.

Design notes:
- Roles are enforced via a single `role` column + RBAC checks in the service
  layer (not separate tables per role) — simpler joins, easier RBAC middleware.
- Money fields (consultation fees) stored as integers in paise/rupees, never
  float, to avoid rounding errors.
- All PII-adjacent fields are nullable-optional and access is gated by RBAC;
  this schema does not itself encrypt at rest — encryption is handled at the
  DB/disk layer per the security milestone.
"""

import enum
import uuid

from sqlalchemy import (
    String,
    Enum,
    ForeignKey,
    Boolean,
    Integer,
    Text,
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin, GUID


class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    DOCTOR = "doctor"
    ASHA_WORKER = "asha_worker"
    ADMIN = "admin"


class ConsultationTier(str, enum.Enum):
    FREE = "free"
    RS_20 = "rs_20"
    RS_50 = "rs_50"
    RS_100 = "rs_100"


class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(
        String(150)
    )

    phone_number: Mapped[str] = mapped_column(
        String(15),
        unique=True,
        index=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(150),
        unique=True,
        nullable=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255)
    )

    # Explicitly use enum VALUES for PostgreSQL:
    # citizen, doctor, asha_worker, admin
    # instead of enum NAMES:
    # CITIZEN, DOCTOR, ASHA_WORKER, ADMIN
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
            name="userrole",
        ),
        default=UserRole.CITIZEN,
    )

    preferred_language: Mapped[str] = mapped_column(
        String(10),
        default="en",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    doctor_profile: Mapped["DoctorProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
    )


class DoctorProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "doctor_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("users.id"),
        unique=True,
    )

    medical_council_reg_no: Mapped[str] = mapped_column(
        String(50),
        unique=True,
    )

    specialization: Mapped[str] = mapped_column(
        String(100)
    )

    years_experience: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_verified_by_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    default_consultation_tier: Mapped[ConsultationTier] = mapped_column(
        Enum(
            ConsultationTier,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
            name="consultationtier",
        ),
        default=ConsultationTier.FREE,
    )

    average_rating: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    user: Mapped["User"] = relationship(
        back_populates="doctor_profile"
    )

    videos: Mapped[list["EducationalVideo"]] = relationship(
        back_populates="doctor"
    )

class Appointment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "appointments"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("doctor_profiles.id"),
        nullable=False,
    )

    scheduled_at: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    consultation_tier: Mapped[ConsultationTier] = mapped_column(
        Enum(
            ConsultationTier,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
            name="consultationtier",
        ),
        nullable=False,
    )

    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(
            AppointmentStatus,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
            name="appointmentstatus",
        ),
        nullable=False,
        server_default="pending",
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

class EducationalVideo(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "educational_videos"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("doctor_profiles.id"),
    )

    title: Mapped[str] = mapped_column(
        String(200)
    )
    doctor: Mapped["DoctorProfile"] = relationship(
    back_populates="videos"
    )

   

class ChatSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en",
    )


class ChatMessage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chat_sessions.id"),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    sources: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    confidence_score: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    was_emergency_flagged: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

