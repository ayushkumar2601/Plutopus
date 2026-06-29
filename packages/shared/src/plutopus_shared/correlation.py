from typing import List
from sqlalchemy.orm import Session
from plutopus_shared.models import Metric, Interface, Device, Tunnel

def get_metrics_for_tunnel(db: Session, tunnel_id: str, limit: int = 100) -> List[Metric]:
    """
    Returns recent time-series metrics linked to a specific tunnel path.
    """
    return db.query(Metric).filter(Metric.target_id == tunnel_id).order_by(Metric.timestamp.desc()).limit(limit).all()

def get_metrics_for_device(db: Session, device_id: str, limit: int = 100) -> List[Metric]:
    """
    Returns recent metrics corresponding to any interface associated with a device.
    """
    interfaces = db.query(Interface).filter(Interface.device_id == device_id).all()
    intf_ids = [i.id for i in interfaces]
    if not intf_ids:
        return []
    return db.query(Metric).filter(Metric.target_id.in_(intf_ids)).order_by(Metric.timestamp.desc()).limit(limit).all()

def get_metrics_for_site(db: Session, site_id: str, limit: int = 200) -> List[Metric]:
    """
    Returns all metrics associated with a site (including all device interfaces and tunnels).
    """
    devices = db.query(Device).filter(Device.site_id == site_id).all()
    dev_ids = [d.id for d in devices]
    if not dev_ids:
        return []

    interfaces = db.query(Interface).filter(Interface.device_id.in_(dev_ids)).all()
    intf_ids = [i.id for i in interfaces]
    if not intf_ids:
        return []

    # Get tunnels terminating at these interfaces
    tunnels = db.query(Tunnel).filter(
        (Tunnel.src_interface_id.in_(intf_ids)) | 
        (Tunnel.dst_interface_id.in_(intf_ids))
    ).all()
    tun_ids = [t.id for t in tunnels]

    target_ids = intf_ids + tun_ids
    return db.query(Metric).filter(Metric.target_id.in_(target_ids)).order_by(Metric.timestamp.desc()).limit(limit).all()
