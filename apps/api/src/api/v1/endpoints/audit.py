from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from plutopus_shared import get_db, AuditLog
from core.auth import RoleChecker, UserPayload
from typing import List, Dict, Any, Optional

router = APIRouter()

@router.get("/logs", response_model=List[Dict[str, Any]])
def list_audit_logs(
    username: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    user: UserPayload = Depends(RoleChecker(["admin"]))
):
    """
    List immutable audit log trail with pagination and filters.
    Only users with 'admin' role may retrieve compliance trails.
    """
    q = db.query(AuditLog)
    if username:
        q = q.filter(AuditLog.username == username)
    if action:
        q = q.filter(AuditLog.action == action)
        
    logs = q.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
    
    return [
        {
            "id": l.id,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None,
            "username": l.username,
            "action": l.action,
            "resource": l.resource,
            "resource_id": l.resource_id,
            "result": l.result,
            "source_ip": l.source_ip
        }
        for l in logs
    ]
