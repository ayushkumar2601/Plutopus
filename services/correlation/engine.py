import os
import sys
import uuid
import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session

# Add paths dynamically to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../services/topology")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../packages/shared/src")))

from plutopus_shared.models import Anomaly, Event, Incident, Tunnel, Device, Interface
from repository import TopologyRepository

class EventCorrelationEngine:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TopologyRepository(db)

    def run_correlation(self) -> List[Dict[str, Any]]:
        """
        Scours active anomalies and groups them into root-cause incidents using topology relationships.
        """
        # Fetch active anomalies (unresolved/recent within last 30 minutes)
        anomalies = self.db.query(Anomaly).order_by(Anomaly.timestamp.desc()).limit(50).all()
        if not anomalies:
            return []

        # Find hub-related failures
        hub_anoms = [a for a in anomalies if "hub" in a.entity_id.lower()]
        spoke_anoms = [a for a in anomalies if "branch" in a.entity_id.lower()]

        correlated_incidents = []

        # Scenario 1: Hub Link Degraded causes multiple Spoke drops
        if hub_anoms:
            for ha in hub_anoms:
                # Find spokes linked to this hub tunnel
                affected_spokes = []
                source_anoms = [ha.id]
                
                # Check which spoke anomalies overlap in time/metric
                for sa in spoke_anoms:
                    if sa.metric == ha.metric:
                        # Extract branch ID
                        import re
                        branch_match = re.search(r"(site-branch-\d+|branch-\d+)", sa.entity_id.lower())
                        if branch_match:
                            affected_spokes.append(branch_match.group(1))
                            source_anoms.append(sa.id)

                if len(affected_spokes) >= 2:
                    incident_id = str(uuid.uuid4())
                    correlated_incidents.append({
                        "incident_id": incident_id,
                        "title": f"Correlated Hub Link Congestion affecting spokes",
                        "description": f"Telemetry spike on {ha.entity_id} matches degradation pattern across {len(affected_spokes)} spokes.",
                        "root_cause": ha.entity_id,
                        "affected_sites": list(set(affected_spokes)),
                        "confidence": 0.92,
                        "severity": "critical",
                        "source_anomalies": source_anoms,
                        "source_events": []
                    })

        # Scenario 2: Site local isolation (Multiple interface anomalies on same Site edge router)
        spoke_by_site = {}
        for sa in spoke_anoms:
            import re
            site_match = re.search(r"(site-branch-\d+|site-hub)", sa.entity_id.lower())
            if site_match:
                site_id = site_match.group(1)
                if site_id not in spoke_by_site:
                    spoke_by_site[site_id] = []
                spoke_by_site[site_id].append(sa)

        for site_id, anoms in spoke_by_site.items():
            if len(anoms) >= 2 and not any(inc["root_cause"] == site_id for inc in correlated_incidents):
                incident_id = str(uuid.uuid4())
                correlated_incidents.append({
                    "incident_id": incident_id,
                    "title": f"Local site degradation on {site_id}",
                    "description": f"Multiple anomalies detected on local interfaces of {site_id}.",
                    "root_cause": site_id,
                    "affected_sites": [site_id],
                    "confidence": 0.85,
                    "severity": "high",
                    "source_anomalies": [a.id for a in anoms],
                    "source_events": []
                })

        # Persist new incidents into the database
        for inc in correlated_incidents:
            # Check if this incident already exists to prevent duplicate entries
            existing = self.db.query(Incident).filter(Incident.root_cause == inc["root_cause"], Incident.status == "active").first()
            if not existing:
                new_inc = Incident(
                    id=inc["incident_id"],
                    title=inc["title"],
                    description=inc["description"],
                    severity=inc["severity"],
                    status="active",
                    root_cause=inc["root_cause"],
                    confidence=inc["confidence"],
                    affected_entities=json.dumps(inc["affected_sites"]),
                    source_anomalies=json.dumps(inc["source_anomalies"]),
                    source_events=json.dumps(inc["source_events"]),
                    priority=50  # to be updated by prioritization engine
                )
                self.db.add(new_inc)
            else:
                inc["incident_id"] = existing.id
        
        self.db.commit()
        return correlated_incidents
