import os
import sys
import json
from datetime import datetime
from sqlalchemy.orm import Session

# Add topology path dynamically to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../services/topology")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../packages/shared/src")))

from plutopus_shared.models import Site, Device, Interface, Tunnel, Metric, Event, Forecast, Anomaly, RiskScore
from repository import TopologyRepository
from health import TopologyHealthEngine

class CopilotContextEngine:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TopologyRepository(db)
        self.health_eng = TopologyHealthEngine(db)

    def get_site_context(self, site_id: str) -> dict:
        """
        Gathers comprehensive details, active anomalies, risk indexes, and connected sites.
        """
        site = self.repo.get_site(site_id)
        if not site:
            return {}

        devices = self.repo.get_site_devices(site_id)
        dev_ids = [d.id for d in devices]
        
        interfaces = self.db.query(Interface).filter(Interface.device_id.in_(dev_ids)).all()
        intf_ids = [i.id for i in interfaces]
        
        tunnels = self.db.query(Tunnel).filter(
            (Tunnel.src_interface_id.in_(intf_ids)) | 
            (Tunnel.dst_interface_id.in_(intf_ids))
        ).all()
        tun_ids = [t.id for t in tunnels]

        # Get latest risk score
        risk = self.db.query(RiskScore).filter(
            RiskScore.entity_id == site_id,
            RiskScore.entity_type == "site"
        ).order_by(RiskScore.timestamp.desc()).first()

        risk_score = risk.risk_score if risk else 0
        risk_level = risk.risk_level if risk else "low"
        signals = json.loads(risk.signals) if risk and risk.signals else []

        # Get active anomalies on interfaces or tunnels
        anoms = self.db.query(Anomaly).filter(
            Anomaly.entity_id.in_(intf_ids + tun_ids)
        ).order_by(Anomaly.timestamp.desc()).limit(10).all()

        anom_list = [
            {"id": a.id, "entity_id": a.entity_id, "metric": a.metric, "severity": a.severity, "description": a.description}
            for a in anoms
        ]

        # Get connected neighbor sites via tunnels
        connected_sites = []
        for t in tunnels:
            src_device = self.db.query(Device).filter(Device.id == self.db.query(Interface).filter(Interface.id == t.src_interface_id).first().device_id).first()
            dst_device = self.db.query(Device).filter(Device.id == self.db.query(Interface).filter(Interface.id == t.dst_interface_id).first().device_id).first()
            
            if src_device and src_device.site_id != site_id:
                connected_sites.append(src_device.site_id)
            if dst_device and dst_device.site_id != site_id:
                connected_sites.append(dst_device.site_id)

        # Unique connections
        connected_sites = list(set(connected_sites))

        return {
            "site_id": site_id,
            "name": site.name,
            "role": site.role,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "signals": signals,
            "devices": [d.id for d in devices],
            "active_anomalies": anom_list,
            "connected_sites": connected_sites
        }

    def get_tunnel_context(self, tunnel_id: str) -> dict:
        """
        Gathers stats, latest loss/latency metrics, forecasted values, and Z-score anomalies.
        """
        tunnel = self.db.query(Tunnel).filter(Tunnel.id == tunnel_id).first()
        if not tunnel:
            return {}

        # Latency metric
        lat_m = self.db.query(Metric).filter(
            Metric.target_id == tunnel_id,
            Metric.name == "latency"
        ).order_by(Metric.timestamp.desc()).first()

        # Loss metric
        loss_m = self.db.query(Metric).filter(
            Metric.target_id == tunnel_id,
            Metric.name == "packet_loss"
        ).order_by(Metric.timestamp.desc()).first()

        # Forecast latency
        lat_f = self.db.query(Forecast).filter(
            Forecast.target_id == tunnel_id,
            Forecast.metric == "latency"
        ).order_by(Forecast.timestamp.desc()).first()

        # Forecast loss
        loss_f = self.db.query(Forecast).filter(
            Forecast.target_id == tunnel_id,
            Forecast.metric == "packet_loss"
        ).order_by(Forecast.timestamp.desc()).first()

        # Risk score
        risk = self.db.query(RiskScore).filter(
            RiskScore.entity_id == tunnel_id,
            RiskScore.entity_type == "tunnel"
        ).order_by(RiskScore.timestamp.desc()).first()

        risk_score = risk.risk_score if risk else 0
        risk_level = risk.risk_level if risk else "low"
        signals = json.loads(risk.signals) if risk and risk.signals else []

        # Anomalies
        anoms = self.db.query(Anomaly).filter(
            Anomaly.entity_id == tunnel_id
        ).order_by(Anomaly.timestamp.desc()).limit(5).all()

        return {
            "tunnel_id": tunnel_id,
            "status": tunnel.status,
            "metrics": {
                "latency": lat_m.value if lat_m else 0.0,
                "packet_loss": loss_m.value if loss_m else 0.0
            },
            "forecasts": {
                "latency_15m": lat_f.forecast_15m if lat_f else 0.0,
                "latency_30m": lat_f.forecast_30m if lat_f else 0.0,
                "latency_60m": lat_f.forecast_60m if lat_f else 0.0,
                "packet_loss_15m": loss_f.forecast_15m if loss_f else 0.0,
                "packet_loss_30m": loss_f.forecast_30m if loss_f else 0.0,
                "packet_loss_60m": loss_f.forecast_60m if loss_f else 0.0,
                "confidence": lat_f.confidence if lat_f else 0.85
            },
            "risk_score": risk_score,
            "risk_level": risk_level,
            "signals": signals,
            "anomalies": [{"severity": a.severity, "metric": a.metric, "description": a.description} for a in anoms]
        }
