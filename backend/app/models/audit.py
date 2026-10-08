"""
Audit log — records security-sensitive actions (auth events, role changes,
doctor verification, video approval, admin access) with actor, action, and
target. Deliberately append-only at the application level: no update/delete
endpoint is ever exposed for this table.
"""
import uuid
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin, GUID


class AuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "audit_logs"

    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    action: Mapped[str] = mapped_column(String(100))  # e.g. "doctor.verify", "user.login", "video.approve"
    target_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON-encoded extra context
