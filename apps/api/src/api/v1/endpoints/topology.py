import os
import sys
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

# Add topology path dynamically to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../services/topology")))

from plutopus_shared import get_db
from repository import TopologyRepository
from intelligence import TopologyIntelligenceService
from health import TopologyHealthEngine
from schemas.api_models import TopologyResponseSchema

router = APIRouter()

@router.get("/", response_model=TopologyResponseSchema)
def get_topology_legacy(db: Session = Depends(get_db)):
    """
    Legacy endpoint for basic layout schema.
    """
    repo = TopologyRepository(db)
    # Reuses the Graph Engine layout mapping from Phase 1
    nodes = []
    links = []
    
    for node_id, data in repo.engine.graph.nodes(data=True):
        nodes.append({
            "id": node_id,
            "label": data.get("label", node_id),
            "type": data.get("type", "unknown"),
            "status": data.get("status", "up")
        })
        
    for u, v, data in repo.engine.graph.edges(data=True):
        if data.get("relation") == "INTERFACE_CONNECTED_TO":
            links.append({
                "id": data.get("tunnel_id", f"link-{u}-{v}"),
                "source": u,
                "target": v,
                "status": data.get("status", "up")
            })
            
    return {"nodes": nodes, "links": links}

@router.get("/graph", response_model=Dict[str, Any])
def get_graph(db: Session = Depends(get_db)):
    """
    Retrieve the full compiled topology graph nodes and edge relationships.
    """
    repo = TopologyRepository(db)
    nodes = []
    edges = []
    
    for node_id, data in repo.engine.graph.nodes(data=True):
        nodes.append({"id": node_id, **data})
        
    for u, v, data in repo.engine.graph.edges(data=True):
        edges.append({"source": u, "target": v, **data})
        
    return {"nodes": nodes, "edges": edges}

@router.get("/sites/{id}", response_model=Dict[str, Any])
def get_site_details(id: str, db: Session = Depends(get_db)):
    """
    Retrieve deep topology info, health metrics, and devices for a site.
    """
    repo = TopologyRepository(db)
    health_eng = TopologyHealthEngine(db)
    
    site = repo.get_site(id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
        
    devices = repo.get_site_devices(id)
    tunnels = repo.get_site_tunnels(id)
    status = health_eng.calculate_site_status(id)
    
    return {
        "id": site.id,
        "name": site.name,
        "role": site.role,
        "status": status,
        "devices_count": len(devices),
        "tunnels_count": len(tunnels),
        "devices": [{"id": d.id, "name": d.name, "role": d.role, "ip": d.ip} for d in devices]
    }

@router.get("/devices/{id}", response_model=Dict[str, Any])
def get_device_details(id: str, db: Session = Depends(get_db)):
    """
    Retrieve interface list, parent site, and health for a device.
    """
    repo = TopologyRepository(db)
    health_eng = TopologyHealthEngine(db)
    
    device = repo.get_device(id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    interfaces = repo.db.query(Interface).filter(Interface.device_id == id).all()
    intf_details = []
    for i in interfaces:
        intf_status = health_eng.calculate_interface_status(i.id)
        intf_details.append({
            "id": i.id,
            "name": i.name,
            "type": i.type,
            "status": intf_status
        })
        
    return {
        "id": device.id,
        "name": device.name,
        "site_id": device.site_id,
        "role": device.role,
        "ip": device.ip,
        "interfaces": intf_details
    }

@router.get("/path", response_model=Dict[str, Any])
def get_path(
    source_site: str = Query(..., description="ID of source site"),
    destination_site: str = Query(..., description="ID of destination site"),
    db: Session = Depends(get_db)
):
    """
    Calculate topological shortest path route between sites.
    """
    repo = TopologyRepository(db)
    path_data = repo.get_tunnel_path(source_site, destination_site)
    if not path_data.get("path"):
        raise HTTPException(status_code=404, detail="No path found between selected sites")
    return path_data

@router.get("/neighbors", response_model=List[Dict[str, Any]])
def get_neighbors(
    node_id: str = Query(..., description="ID of node in graph"),
    db: Session = Depends(get_db)
):
    """
    Retrieve adjacent neighbors and edge relationship links.
    """
    repo = TopologyRepository(db)
    return repo.get_neighbors(node_id)

@router.get("/intelligence", response_model=Dict[str, Any])
def get_topology_intelligence(db: Session = Depends(get_db)):
    """
    Retrieve centrality, critical paths, and underlay overlay analysis.
    """
    service = TopologyIntelligenceService(db)
    health_eng = TopologyHealthEngine(db)
    
    intel = service.get_system_intelligence()
    network_health = health_eng.calculate_network_status()
    
    return {
        **intel,
        "network_health": network_health
    }
