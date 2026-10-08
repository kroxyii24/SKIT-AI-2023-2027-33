from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def log_action(
    db: Session,
    action: str,
    actor_user_id: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    ip_address: str | None = None,
    details: str | None = None,
) -> None:
    """
    Writes an audit entry. Callers are responsible for committing the
    surrounding transaction — this only adds to the session so it commits
    atomically with the action it's logging (avoids a state where the action
    succeeds but the audit write is lost, or vice versa).
    """
    db.add(AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        ip_address=ip_address,
        details=details,
    ))
