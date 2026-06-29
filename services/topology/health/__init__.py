from typing import Dict, Any, List
from sqlalchemy.orm import Session
from plutopus_shared.models import Site, Device, Interface, Tunnel, Metric, Event

class TopologyHealthEngine:
    def __init__(self, db: Session):
        self.db = db

    def calculate_interface_status(self, intf_id: str) -> str:
        """
        Derives interface health using status database fields and recent utilization metrics.
        """
        intf = self.db.query(Interface).filter(Interface.id == intf_id).first()
        if not intf:
            return "unknown"
            
        if intf.status == "down":
            return "critical"

        # Check latest utilization metric
        latest_util = self.db.query(Metric).filter(
            Metric.target_id == intf_id,
            Metric.name == "utilization"
        ).order_by(Metric.timestamp.desc()).first()

        if latest_util:
            if latest_util.value >= 90.0:
                return "warning"
            elif latest_util.value >= 75.0:
                return "degraded"
                
        return "healthy"

    def calculate_tunnel_status(self, tunnel_id: str) -> str:
        """
        Derives tunnel health from recent latency and packet loss metrics.
        Worst-case health is returned.
        """
        tunnel = self.db.query(Tunnel).filter(Tunnel.id == tunnel_id).first()
        if not tunnel:
            return "unknown"

        if tunnel.status == "down":
            return "critical"

        status = "healthy"

        # Check packet loss
        latest_loss = self.db.query(Metric).filter(
            Metric.target_id == tunnel_id,
            Metric.name == "packet_loss"
        ).order_by(Metric.timestamp.desc()).first()

        if latest_loss:
            if latest_loss.value >= 5.0:
                status = "critical"
            elif latest_loss.value >= 1.0:
                status = "warning"

        if status == "critical":
            return status

        # Check latency
        latest_latency = self.db.query(Metric).filter(
            Metric.target_id == tunnel_id,
            Metric.name == "latency"
        ).order_by(Metric.timestamp.desc()).first()

        if latest_latency:
            if latest_latency.value >= 150.0:
                status = "critical"
            elif latest_latency.value >= 80.0:
                status = "degraded"

        return status

    def calculate_site_status(self, site_id: str) -> str:
        """
        Derives site health based on the aggregated health of its terminating tunnels.
        """
        devices = self.db.query(Device).filter(Device.site_id == site_id).all()
        dev_ids = [d.id for d in devices]
        
        interfaces = self.db.query(Interface).filter(Interface.device_id.in_(dev_ids)).all()
        intf_ids = [i.id for i in interfaces]
        
        tunnels = self.db.query(Tunnel).filter(
            (Tunnel.src_interface_id.in_(intf_ids)) | 
            (Tunnel.dst_interface_id.in_(intf_ids))
        ).all()

        if not tunnels:
            return "healthy"

        tunnel_statuses = [self.calculate_tunnel_status(t.id) for t in tunnels]
        
        if all(s == "critical" for s in tunnel_statuses):
            return "critical"
        elif any(s == "critical" for s in tunnel_statuses):
            return "degraded"
        elif any(s in ["warning", "degraded"] for s in tunnel_statuses):
            return "warning"
            
        return "healthy"

    def calculate_network_status(self) -> Dict[str, Any]:
        """
        Computes overall global network health stats.
        """
        sites = self.db.query(Site).all()
        site_statuses = {s.id: self.calculate_site_status(s.id) for s in sites}
        
        critical_count = sum(1 for s in site_statuses.values() if s == "critical")
        degraded_count = sum(1 for s in site_statuses.values() if s == "degraded")
        warning_count = sum(1 for s in site_statuses.values() if s == "warning")
        
        status = "healthy"
        if critical_count > 0:
            status = "critical"
        elif degraded_count > 0:
            status = "degraded"
        elif warning_count > 0:
            status = "warning"
            
        return {
            "status": status,
            "sites_health": site_statuses,
            "summary": {
                "total": len(sites),
                "critical": critical_count,
                "degraded": degraded_count,
                "warning": warning_count,
                "healthy": len(sites) - (critical_count + degraded_count + warning_count)
            }
        }
