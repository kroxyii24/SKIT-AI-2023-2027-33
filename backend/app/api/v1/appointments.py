"""
Appointment booking.

Key business rules enforced here (not just at the DB level):
  1. A patient cannot book a doctor who isn't admin-verified.
  2. Double-booking prevention: a doctor cannot have two CONFIRMED/PENDING
     appointments at the exact same scheduled_at slot.
  3. Only the assigned doctor (or an admin) can change an appointment's status.
  4. Patients see only their own appointments; doctors see only their own
     patient list — no cross-visibility, enforced via query filters, not
     just response filtering (avoids leaking data even transiently).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.rbac import get_current_user, TokenPayload
from app.db.session import get_db
from app.models.domain import Appointment, DoctorProfile, AppointmentStatus
from app.schemas.appointment import AppointmentCreate, AppointmentOut, AppointmentStatusUpdate

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("/", response_model=AppointmentOut, status_code=201)
def book_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    user: TokenPayload = Depends(get_current_user),
):
    doctor = db.get(DoctorProfile, payload.doctor_id)
    if not doctor or not doctor.is_verified_by_admin:
        raise HTTPException(status_code=404, detail="Doctor not found or not available for booking")

    scheduled_iso = payload.scheduled_at.isoformat()
    conflict = db.execute(
        select(Appointment).where(
            Appointment.doctor_id == payload.doctor_id,
            Appointment.scheduled_at == scheduled_iso,
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]),
        )
    ).scalar_one_or_none()
    if conflict:
        raise HTTPException(status_code=409, detail="This time slot is no longer available")

    appointment = Appointment(
        patient_id=user.sub,
        doctor_id=payload.doctor_id,
        scheduled_at=scheduled_iso,
        consultation_tier=payload.consultation_tier,
        notes=payload.notes,
        status=AppointmentStatus.PENDING,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/me", response_model=list[AppointmentOut])
def my_appointments(db: Session = Depends(get_db), user: TokenPayload = Depends(get_current_user)):
    if user.role == "doctor":
        doctor = db.execute(select(DoctorProfile).where(DoctorProfile.user_id == user.sub)).scalar_one_or_none()
        if not doctor:
            return []
        stmt = select(Appointment).where(Appointment.doctor_id == doctor.id)
    else:
        stmt = select(Appointment).where(Appointment.patient_id == user.sub)
    return db.execute(stmt).scalars().all()


@router.patch("/{appointment_id}/status", response_model=AppointmentOut)
def update_status(
    appointment_id: str,
    payload: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    user: TokenPayload = Depends(get_current_user),
):
    appointment = db.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    doctor = db.execute(
        select(DoctorProfile).where(DoctorProfile.user_id == user.sub)
    ).scalar_one_or_none()
    is_owning_doctor = doctor is not None and doctor.id == appointment.doctor_id
    if user.role != "admin" and not is_owning_doctor:
        raise HTTPException(status_code=403, detail="Not authorized to update this appointment")

    appointment.status = payload.status
    db.commit()
    db.refresh(appointment)
    return appointment
