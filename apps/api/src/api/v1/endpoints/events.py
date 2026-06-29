from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from plutopus_shared import get_db, Event
from schemas.api_models import EventSchema

router = APIRouter()

@router.get("/", response_model=List[EventSchema])
def get_events(
    device_id: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Retrieve network events with optional filtering.
    """
    query = db.query(Event)
    if device_id:
        query = query.filter(Event.device_id == device_id)
    if severity:
        query = query.filter(Event.severity == severity.lower())
    events = query.order_by(Event.timestamp.desc()).offset(skip).limit(limit).all()
    return events
