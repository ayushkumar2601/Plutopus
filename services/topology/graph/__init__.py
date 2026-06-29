import networkx as nx
from sqlalchemy.orm import Session
from plutopus_shared.models import Site, Device, Interface, Tunnel

class TopologyGraphEngine:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_from_db(self, db: Session):
        """
        Builds the NetworkX graph from database records.
        """
        self.graph.clear()
        
        # 1. Sites
        sites = db.query(Site).all()
        for site in sites:
            self.graph.add_node(
                site.id,
                label=site.name,
                type="site",
                role=site.role
            )
            
        # 2. Devices
        devices = db.query(Device).all()
        for device in devices:
            self.graph.add_node(
                device.id,
                label=device.name,
                type="device",
                role=device.role,
                ip=device.ip
            )
            # Relationship: SITE_CONTAINS_DEVICE
            self.graph.add_edge(
                device.site_id,
                device.id,
                relation="SITE_CONTAINS_DEVICE"
            )
            # Back-link to query parent site from device node
            self.graph.add_edge(
                device.id,
                device.site_id,
                relation="DEVICE_BELONGS_TO_SITE"
            )
            
        # 3. Interfaces
        interfaces = db.query(Interface).all()
        for intf in interfaces:
            self.graph.add_node(
                intf.id,
                label=intf.name,
                type="interface",
                intf_type=intf.type,
                status=intf.status
            )
            # Relationship: DEVICE_HAS_INTERFACE
            self.graph.add_edge(
                intf.device_id,
                intf.id,
                relation="DEVICE_HAS_INTERFACE"
            )
            # Back-link
            self.graph.add_edge(
                intf.id,
                intf.device_id,
                relation="INTERFACE_BELONGS_TO_DEVICE"
            )
            
        # 4. Tunnels
        tunnels = db.query(Tunnel).all()
        for tunnel in tunnels:
            self.graph.add_node(
                tunnel.id,
                type="tunnel",
                status=tunnel.status
            )
            # Relationship: INTERFACE_CONNECTED_TO (connecting interfaces together via tunnel)
            self.graph.add_edge(
                tunnel.src_interface_id,
                tunnel.dst_interface_id,
                relation="INTERFACE_CONNECTED_TO",
                tunnel_id=tunnel.id,
                status=tunnel.status
            )
            self.graph.add_edge(
                tunnel.dst_interface_id,
                tunnel.src_interface_id,
                relation="INTERFACE_CONNECTED_TO",
                tunnel_id=tunnel.id,
                status=tunnel.status
            )
            # Relationship: TUNNEL_TERMINATES_AT
            self.graph.add_edge(
                tunnel.id,
                tunnel.src_interface_id,
                relation="TUNNEL_TERMINATES_AT"
            )
            self.graph.add_edge(
                tunnel.id,
                tunnel.dst_interface_id,
                relation="TUNNEL_TERMINATES_AT"
            )

    def get_shortest_path(self, source_site: str, dest_site: str):
        """
        Calculates the shortest topological path between source and destination site.
        """
        try:
            # Run shortest path over undirected layout to support traversing spoke-hub-spoke
            undirected_graph = self.graph.to_undirected()
            raw_path = nx.shortest_path(undirected_graph, source=source_site, target=dest_site)
            
            # Extract list of sites in path order
            sites_path = [node for node in raw_path if self.graph.nodes[node].get("type") == "site"]
            
            # Extract tunnels crossed along the path
            tunnels_crossed = []
            for u, v in zip(raw_path[:-1], raw_path[1:]):
                edge_data = undirected_graph.get_edge_data(u, v)
                if edge_data and "tunnel_id" in edge_data:
                    tunnels_crossed.append(edge_data["tunnel_id"])
                    
            return {
                "path": sites_path,
                "hops": max(0, len(sites_path) - 1),
                "tunnels": list(set(tunnels_crossed))
            }
        except nx.NetworkXNoPath:
            return {"path": [], "hops": 0, "tunnels": []}
        except Exception:
            return {"path": [], "hops": 0, "tunnels": []}
