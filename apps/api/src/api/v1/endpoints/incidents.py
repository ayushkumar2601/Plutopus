import os
import sys
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Add correlation and integration paths dynamically to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../services/correlation")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../services/integrations")))

from plutopus_shared import get_db, Incident, Anomaly, Event, Site, Device
from core.auth import get_current_user, RoleChecker, UserPayload
from engine import EventCorrelationEngine
from prioritization import AlertPrioritizationEngine
from webhooks import WebhookIntegrationService
from core.metrics import WEBHOOK_DELIVERY_TOTAL, INCIDENTS_GENERATED_TOTAL

router = APIRouter()

# Schema for Webhook payloads
class WebhookPayload(BaseModel):
    url: str
    incident_id: str

class ExportRequest(BaseModel):
    incident_id: str
    target_url: str

class InboundAlertPayload(BaseModel):
    source: str
    message: str
    severity: str
    device_id: str

@router.get("", response_model=List[Dict[str, Any]])
def list_incidents(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity_filter: Optional[str] = Query(None, alias="severity"),
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    user: UserPayload = Depends(RoleChecker(["admin", "operator", "viewer"]))
):
    """
    List incident objects with pagination and filters.
    """
    q = db.query(Incident)
    if status_filter:
        q = q.filter(Incident.status == status_filter)
    if severity_filter:
        q = q.filter(Incident.severity == severity_filter)
        
    incidents = q.order_by(Incident.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        {
            "id": i.id,
            "title": i.title,
            "description": i.description,
            "severity": i.severity,
            "priority": i.priority,
            "status": i.status,
            "root_cause": i.root_cause,
            "confidence": i.confidence,
            "affected_entities": json.loads(i.affected_entities) if i.affected_entities else [],
            "source_anomalies": json.loads(i.source_anomalies) if i.source_anomalies else [],
            "source_events": json.loads(i.source_events) if i.source_events else [],
            "created_at": i.created_at,
            "updated_at": i.updated_at
        }
        for i in incidents
    ]

@router.get("/correlated", response_model=List[Dict[str, Any]])
def trigger_correlation_run(
    db: Session = Depends(get_db),
    user: UserPayload = Depends(RoleChecker(["admin", "operator"]))
):
    """
    Triggers correlation pipeline to aggregate current anomalies into incidents.
    """
    correlator = EventCorrelationEngine(db)
    new_incidents = correlator.run_correlation()
    
    # Calculate priority rankings for each correlated incident
    for inc in new_incidents:
        db_inc = db.query(Incident).filter(Incident.id == inc["incident_id"]).first()
        if db_inc:
            # Gather variables for prioritization calculation
            affected_sites = json.loads(db_inc.affected_entities) if db_inc.affected_entities else []
            criticality = "medium"
            if affected_sites:
                # Find maximum criticality of affected sites
                site_objs = db.query(Site).filter(Site.id.in_(affected_sites)).all()
                if site_objs:
                    # Map enum rankings: mission_critical > high > medium > low
                    crit_map = {"mission_critical": 3, "high": 2, "medium": 1, "low": 0}
                    max_crit = max(site_objs, key=lambda s: crit_map.get(s.business_criticality, 1))
                    criticality = max_crit.business_criticality

            # Estimate priority
            priority_data = AlertPrioritizationEngine.calculate_priority(
                risk_score=90,  # default placeholder or calculated from anomalies
                confidence=db_inc.confidence,
                time_to_impact_mins=30,  # forecast lead window
                business_criticality=criticality,
                affected_nodes_count=len(affected_sites)
            )
            
            db_inc.priority = priority_data["priority"]
            # Map incident severity to priority level
            db_inc.severity = priority_data["level"]
            
            db.commit()
            INCIDENTS_GENERATED_TOTAL.labels(severity=db_inc.severity).inc()

    # Re-fetch active incidents
    return list_incidents(status_filter="active", db=db, user=user)

@router.get("/{incident_id}", response_model=Dict[str, Any])
def get_incident_details(
    incident_id: str,
    db: Session = Depends(get_db),
    user: UserPayload = Depends(RoleChecker(["admin", "operator", "viewer"]))
):
    """
    Fetch a single incident by ID.
    """
    i = db.query(Incident).filter(Incident.id == incident_id).first()
    if not i:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
        
    return {
        "id": i.id,
        "title": i.title,
        "description": i.description,
        "severity": i.severity,
        "priority": i.priority,
        "status": i.status,
        "root_cause": i.root_cause,
        "confidence": i.confidence,
        "affected_entities": json.loads(i.affected_entities) if i.affected_entities else [],
        "source_anomalies": json.loads(i.source_anomalies) if i.source_anomalies else [],
        "source_events": json.loads(i.source_events) if i.source_events else [],
        "created_at": i.created_at,
        "updated_at": i.updated_at
    }

@router.post("/export", response_model=Dict[str, Any])
def export_incident(
    req: ExportRequest,
    db: Session = Depends(get_db),
    user: UserPayload = Depends(RoleChecker(["admin", "operator"]))
):
    """
    Exports a completed incident record to an external webhook system.
    """
    inc = db.query(Incident).filter(Incident.id == req.incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    payload = {
        "event": "incident.correlated",
        "incident_id": inc.id,
        "title": inc.title,
        "description": inc.description,
        "priority": inc.priority,
        "severity": inc.severity,
        "root_cause": inc.root_cause,
        "affected_entities": json.loads(inc.affected_entities) if inc.affected_entities else [],
        "timestamp": inc.created_at.isoformat()
    }

    success = WebhookIntegrationService.dispatch_webhook(req.target_url, payload)
    
    if success:
        WEBHOOK_DELIVERY_TOTAL.labels(status="success").inc()
        return {"status": "exported", "target": req.target_url}
    else:
        WEBHOOK_DELIVERY_TOTAL.labels(status="failed").inc()
        raise HTTPException(status_code=502, detail="Failed to deliver incident payload to external webhook.")

@router.post("/integrations/webhook", response_model=Dict[str, Any])
def inbound_webhook_alert(
    req: InboundAlertPayload,
    db: Session = Depends(get_db)
):
    """
    Public inbound integration receiver. Inserts inbound alerts into local events table.
    """
    # Verify target device exists
    dev = db.query(Device).filter(Device.id == req.device_id).first()
    if not dev:
        raise HTTPException(status_code=404, detail=f"Device {req.device_id} not found in database inventory.")

    new_evt = Event(
        device_id=req.device_id,
        severity=req.severity,
        message=f"[{req.source.upper()}] {req.message}"
    )
    db.add(new_evt)
    db.commit()
    
    return {"status": "received", "event_id": new_evt.id}
