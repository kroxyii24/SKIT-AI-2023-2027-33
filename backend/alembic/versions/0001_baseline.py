"""baseline schema

Revision ID: 0001_baseline
Revises:
Create Date: 2026-07-18

Generates all core tables: users, doctor_profiles, educational_videos,
appointments, chat_sessions, chat_messages, knowledge_sources.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostgreSQL ENUM types
    user_role = postgresql.ENUM(
        "citizen",
        "doctor",
        "asha_worker",
        "admin",
        name="userrole",
    )

    consultation_tier = postgresql.ENUM(
        "free",
        "rs_20",
        "rs_50",
        "rs_100",
        name="consultationtier",
    )

    appointment_status = postgresql.ENUM(
        "pending",
        "confirmed",
        "completed",
        "cancelled",
        name="appointmentstatus",
    )

    # Users
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "full_name",
            sa.String(150),
            nullable=False,
        ),
        sa.Column(
            "phone_number",
            sa.String(15),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "email",
            sa.String(150),
            unique=True,
            nullable=True,
        ),
        sa.Column(
            "hashed_password",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "role",
            user_role,
            nullable=False,
            server_default="citizen",
        ),
        sa.Column(
            "preferred_language",
            sa.String(10),
            server_default="en",
        ),
        sa.Column(
            "is_active",
            sa.Boolean,
            server_default=sa.true(),
        ),
        sa.Column(
            "is_verified",
            sa.Boolean,
            server_default=sa.false(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_index(
        "ix_users_phone_number",
        "users",
        ["phone_number"],
    )

    # Doctor profiles
    op.create_table(
        "doctor_profiles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            unique=True,
            nullable=False,
        ),
        sa.Column(
            "medical_council_reg_no",
            sa.String(50),
            unique=True,
            nullable=False,
        ),
        sa.Column(
            "specialization",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "years_experience",
            sa.Integer,
            server_default="0",
        ),
        sa.Column(
            "bio",
            sa.Text,
            nullable=True,
        ),
        sa.Column(
            "is_verified_by_admin",
            sa.Boolean,
            server_default=sa.false(),
        ),
        sa.Column(
            "default_consultation_tier",
            consultation_tier,
            server_default="free",
        ),
        sa.Column(
            "average_rating",
            sa.Float,
            server_default="0.0",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Educational videos
    op.create_table(
        "educational_videos",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "doctor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("doctor_profiles.id"),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(200),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text,
            nullable=True,
        ),
        sa.Column(
            "video_url",
            sa.String(500),
            nullable=False,
        ),
        sa.Column(
            "language",
            sa.String(10),
            server_default="en",
        ),
        sa.Column(
            "category",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "is_approved",
            sa.Boolean,
            server_default=sa.false(),
        ),
        sa.Column(
            "view_count",
            sa.Integer,
            server_default="0",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Appointments
    op.create_table(
        "appointments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "patient_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "doctor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("doctor_profiles.id"),
            nullable=False,
        ),
        sa.Column(
            "scheduled_at",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "consultation_tier",
            consultation_tier,
            nullable=False,
        ),
        sa.Column(
            "status",
            appointment_status,
            server_default="pending",
        ),
        sa.Column(
            "notes",
            sa.Text,
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Chat sessions
    op.create_table(
        "chat_sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "language",
            sa.String(10),
            server_default="en",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Chat messages
    op.create_table(
        "chat_messages",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("chat_sessions.id"),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.String(20),
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.Text,
            nullable=False,
        ),
        sa.Column(
            "sources",
            sa.Text,
            nullable=True,
        ),
        sa.Column(
            "confidence_score",
            sa.Float,
            nullable=True,
        ),
        sa.Column(
            "was_emergency_flagged",
            sa.Boolean,
            server_default=sa.false(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # Knowledge sources
    op.create_table(
        "knowledge_sources",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "title",
            sa.String(300),
            nullable=False,
        ),
        sa.Column(
            "publisher",
            sa.String(150),
            nullable=False,
        ),
        sa.Column(
            "source_url",
            sa.String(500),
            nullable=True,
        ),
        sa.Column(
            "file_path",
            sa.String(500),
            nullable=True,
        ),
        sa.Column(
            "is_active",
            sa.Boolean,
            server_default=sa.true(),
        ),
        sa.Column(
            "ingested_chunk_count",
            sa.Integer,
            server_default="0",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("knowledge_sources")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_table("appointments")
    op.drop_table("educational_videos")
    op.drop_table("doctor_profiles")
    op.drop_table("users")

    bind = op.get_bind()

    postgresql.ENUM(
        name="appointmentstatus"
    ).drop(bind, checkfirst=True)

    postgresql.ENUM(
        name="consultationtier"
    ).drop(bind, checkfirst=True)

    postgresql.ENUM(
        name="userrole"
    ).drop(bind, checkfirst=True)