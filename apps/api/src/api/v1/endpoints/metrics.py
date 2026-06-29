from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from plutopus_shared import get_db, Metric
from schemas.api_models import MetricSchema

router = APIRouter()

@router.get("/", response_model=List[MetricSchema])
def get_metrics(
    target_id: Optional[str] = Query(default=None),
    name: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Retrieve telemetry metrics with filtering by target_id and metric name.
    """
    query = db.query(Metric)
    if target_id:
        query = query.filter(Metric.target_id == target_id)
    if name:
        query = query.filter(Metric.name == name)
    metrics = query.order_by(Metric.timestamp.desc()).offset(skip).limit(limit).all()
    return metrics
