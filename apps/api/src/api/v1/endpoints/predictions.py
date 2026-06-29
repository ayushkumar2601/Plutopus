from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from plutopus_shared import get_db, Forecast, Anomaly, RiskScore
import json

router = APIRouter()

@router.get("/predictions", response_model=List[Dict[str, Any]])
def get_predictions(
    target_id: Optional[str] = Query(default=None),
    metric: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Retrieve paginated list of metric forecasts.
    """
    query = db.query(Forecast)
    if target_id:
        query = query.filter(Forecast.target_id == target_id)
    if metric:
        query = query.filter(Forecast.metric == metric)
        
    runs = query.order_by(Forecast.timestamp.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": r.id,
            "target_id": r.target_id,
            "metric": r.metric,
            "current_val": r.current_val,
            "forecast_15m": r.forecast_15m,
            "forecast_30m": r.forecast_30m,
            "forecast_60m": r.forecast_60m,
            "confidence": r.confidence,
            "timestamp": r.timestamp
        }
        for r in runs
    ]

@router.get("/predictions/sites", response_model=List[Dict[str, Any]])
def get_site_predictions(
    site_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Retrieve latest risk index scores for all site instances.
    """
    query = db.query(RiskScore).filter(RiskScore.entity_type == "site")
    if site_id:
        query = query.filter(RiskScore.entity_id == site_id)
        
    scores = query.order_by(RiskScore.timestamp.desc()).all()
    
    seen = set()
    latest_scores = []
    for s in scores:
        if s.entity_id not in seen:
            seen.add(s.entity_id)
            latest_scores.append({
                "id": s.id,
                "entity_id": s.entity_id,
                "risk_score": s.risk_score,
                "risk_level": s.risk_level,
                "signals": json.loads(s.signals) if s.signals else [],
                "timestamp": s.timestamp
            })
    return latest_scores

@router.get("/predictions/tunnels", response_model=List[Dict[str, Any]])
def get_tunnel_predictions(
    tunnel_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Retrieve latest risk index scores for tunnels.
    """
    query = db.query(RiskScore).filter(RiskScore.entity_type == "tunnel")
    if tunnel_id:
        query = query.filter(RiskScore.entity_id == tunnel_id)
        
    scores = query.order_by(RiskScore.timestamp.desc()).all()
    
    seen = set()
    latest_scores = []
    for s in scores:
        if s.entity_id not in seen:
            seen.add(s.entity_id)
            latest_scores.append({
                "id": s.id,
                "entity_id": s.entity_id,
                "risk_score": s.risk_score,
                "risk_level": s.risk_level,
                "signals": json.loads(s.signals) if s.signals else [],
                "timestamp": s.timestamp
            })
    return latest_scores

@router.get("/anomalies", response_model=List[Dict[str, Any]])
def get_anomalies(
    severity: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Retrieve rolling Z-score anomalies detected by background worker.
    """
    query = db.query(Anomaly)
    if severity:
        query = query.filter(Anomaly.severity == severity.lower())
        
    anoms = query.order_by(Anomaly.timestamp.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": a.id,
            "entity_id": a.entity_id,
            "entity_type": a.entity_type,
            "metric": a.metric,
            "severity": a.severity,
            "score": a.score,
            "description": a.description,
            "timestamp": a.timestamp
        }
        for a in anoms
    ]

@router.get("/risk", response_model=List[Dict[str, Any]])
def get_risk_history(
    entity_id: Optional[str] = Query(default=None),
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get historic logs of computed risks.
    """
    query = db.query(RiskScore)
    if entity_id:
        query = query.filter(RiskScore.entity_id == entity_id)
    scores = query.order_by(RiskScore.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": s.id,
            "entity_id": s.entity_id,
            "entity_type": s.entity_type,
            "risk_score": s.risk_score,
            "risk_level": s.risk_level,
            "signals": json.loads(s.signals) if s.signals else [],
            "timestamp": s.timestamp
        }
        for s in scores
    ]

@router.get("/forecast", response_model=Dict[str, Any])
def get_latest_forecast(
    target_id: str = Query(...),
    metric: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Retrieve latest forecasted projection for a specific node interface or tunnel.
    """
    f = db.query(Forecast).filter(
        Forecast.target_id == target_id,
        Forecast.metric == metric
    ).order_by(Forecast.timestamp.desc()).first()
    
    if not f:
        raise HTTPException(status_code=404, detail="No forecast found for this target metric")
        
    return {
        "id": f.id,
        "target_id": f.target_id,
        "metric": f.metric,
        "current_val": f.current_val,
        "forecast_15m": f.forecast_15m,
        "forecast_30m": f.forecast_30m,
        "forecast_60m": f.forecast_60m,
        "confidence": f.confidence,
        "timestamp": f.timestamp
    }
