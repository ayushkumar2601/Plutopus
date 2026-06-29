from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from plutopus_shared.models import Site, Device, Interface, Tunnel
from graph import TopologyGraphEngine

class TopologyRepository:
    def __init__(self, db: Session):
        self.db = db
        self.engine = TopologyGraphEngine()
        self.engine.build_from_db(db)

    def get_site(self, site_id: str) -> Optional[Site]:
        return self.db.query(Site).filter(Site.id == site_id).first()

    def get_device(self, device_id: str) -> Optional[Device]:
        return self.db.query(Device).filter(Device.id == device_id).first()

    def get_site_devices(self, site_id: str) -> List[Device]:
        return self.db.query(Device).filter(Device.site_id == site_id).all()

    def get_site_tunnels(self, site_id: str) -> List[Tunnel]:
        # Tunnels terminate at interfaces, interfaces belong to devices, devices belong to sites.
        devices = self.get_site_devices(site_id)
        device_ids = [d.id for d in devices]
        
        interfaces = self.db.query(Interface).filter(Interface.device_id.in_(device_ids)).all()
        interface_ids = [i.id for i in interfaces]
        
        tunnels = self.db.query(Tunnel).filter(
            (Tunnel.src_interface_id.in_(interface_ids)) | 
            (Tunnel.dst_interface_id.in_(interface_ids))
        ).all()
        return tunnels

    def get_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        """
        Gets directly adjacent nodes and relationship links from the graph.
        """
        neighbors = []
        if node_id in self.engine.graph:
            # Outbound neighbors
            for neighbor_id in self.engine.graph.neighbors(node_id):
                edge_data = self.engine.graph.get_edge_data(node_id, neighbor_id)
                relation = edge_data.get("relation", "CONNECTED_TO")
                node_data = self.engine.graph.nodes[neighbor_id]
                neighbors.append({
                    "id": neighbor_id,
                    "type": node_data.get("type"),
                    "label": node_data.get("label"),
                    "relation": relation
                })
        return neighbors

    def get_tunnel_path(self, source_site: str, dest_site: str) -> Dict[str, Any]:
        """
        Computes shortest path traversal crossing sites/devices/tunnels.
        """
        return self.engine.get_shortest_path(source_site, dest_site)
