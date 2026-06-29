from sqlalchemy.orm import Session
from plutopus_shared import AuditLog

def log_audit_event(
    db: Session,
    username: str,
    action: str,
    resource: str,
    resource_id: str,
    result: str,
    source_ip: str = None
):
    """
    Persists an immutable compliance log entry.
    """
    log = AuditLog(
        username=username,
        action=action,
        resource=resource,
        resource_id=resource_id,
        result=result,
        source_ip=source_ip
    )
    db.add(log)
    db.commit()
