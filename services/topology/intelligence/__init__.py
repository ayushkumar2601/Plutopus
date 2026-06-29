import networkx as nx
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from graph import TopologyGraphEngine
from plutopus_shared.models import Site, Tunnel, Interface, Device

class TopologyIntelligenceService:
    def __init__(self, db: Session):
        self.db = db
        self.engine = TopologyGraphEngine()
        self.engine.build_from_db(db)

    def analyze_site(self, site_id: str) -> Dict[str, Any]:
        """
        Analyzes topological characteristics of a site.
        """
        graph = self.engine.graph
        if site_id not in graph:
            return {"error": "Site not found in graph"}

        # Calculate node degree (count of edges in undirected graph representation)
        undirected = graph.to_undirected()
        degree = undirected.degree(site_id)

        # Count tunnels terminating at this site
        # Terminology: site -> device -> interface -> tunnel
        devices = self.db.query(Device).filter(Device.site_id == site_id).all()
        dev_ids = [d.id for d in devices]
        interfaces = self.db.query(Interface).filter(Interface.device_id.in_(dev_ids)).all()
        intf_ids = [i.id for i in interfaces]
        
        tunnels = self.db.query(Tunnel).filter(
            (Tunnel.src_interface_id.in_(intf_ids)) | 
            (Tunnel.dst_interface_id.in_(intf_ids))
        ).all()

        # Criticality assessment: Hub is critical. Spokes with low connection counts are medium.
        site = self.db.query(Site).filter(Site.id == site_id).first()
        site_role = site.role if site else "spoke"
        
        criticality = "low"
        if site_role == "hub":
            criticality = "high"
        elif len(tunnels) <= 2:
            criticality = "medium"

        connected_sites = []
        for dev_id in dev_ids:
            for neighbor in undirected.neighbors(dev_id):
                n_type = graph.nodes[neighbor].get("type")
                # Find connected peer devices, mapping them back to their sites
                if n_type == "interface":
                    # Check connection via tunnel
                    for sub_neighbor in undirected.neighbors(neighbor):
                        # Connected interface
                        edge_data = undirected.get_edge_data(neighbor, sub_neighbor)
                        if edge_data and "tunnel_id" in edge_data:
                            # Peer interface's device -> site
                            peer_dev_id = list(undirected.neighbors(sub_neighbor))
                            for p_dev in peer_dev_id:
                                if graph.nodes[p_dev].get("type") == "device":
                                    # Get its parent site
                                    p_sites = [s for s in undirected.neighbors(p_dev) if graph.nodes[s].get("type") == "site"]
                                    connected_sites.extend(p_sites)

        return {
            "site": site_id,
            "role": site_role,
            "degree": degree,
            "tunnels_count": len(tunnels),
            "connected_to": list(set(connected_sites) - {site_id}),
            "criticality": criticality
        }

    def get_critical_links(self) -> List[Dict[str, Any]]:
        """
        Determines critical single-point-of-failure or degraded tunnel paths.
        """
        critical_links = []
        tunnels = self.db.query(Tunnel).all()
        for tun in tunnels:
            # If a tunnel status is down, or if it terminates at single-homed spokes, mark it
            if tun.status == "down":
                critical_links.append({
                    "id": tun.id,
                    "reason": "Tunnel status is DOWN",
                    "severity": "critical"
                })
        return critical_links

    def get_system_intelligence(self) -> Dict[str, Any]:
        """
        Aggregates global network intelligence metrics.
        """
        sites = self.db.query(Site).all()
        tunnels = self.db.query(Tunnel).all()
        
        hub_count = len([s for s in sites if s.role == "hub"])
        spoke_count = len([s for s in sites if s.role == "spoke"])
        
        analysis = []
        for s in sites:
            analysis.append(self.analyze_site(s.id))

        return {
            "hubs": hub_count,
            "spokes": spoke_count,
            "total_tunnels": len(tunnels),
            "critical_links": self.get_critical_links(),
            "site_analysis": analysis
        }
