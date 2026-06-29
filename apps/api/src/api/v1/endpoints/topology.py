from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from plutopus_shared import get_db, Site, Device, Tunnel, Interface
from schemas.api_models import TopologyResponseSchema, TopologyNodeSchema, TopologyLinkSchema

router = APIRouter()

@router.get("/", response_model=TopologyResponseSchema)
def get_topology(db: Session = Depends(get_db)):
    """
    Generate graph structure representing network sites, edge devices, and tunnels.
    """
    sites = db.query(Site).all()
    devices = db.query(Device).all()
    tunnels = db.query(Tunnel).all()

    nodes = []
    links = []

    # 1. Add Sites as Nodes
    for site in sites:
        nodes.append(
            TopologyNodeSchema(
                id=site.id,
                label=site.name,
                type=site.role,  # hub, spoke
                status="up"
            )
        )

    # 2. Add Devices as Nodes and Link them to their parent Sites
    for device in devices:
        nodes.append(
            TopologyNodeSchema(
                id=device.id,
                label=device.name,
                type="device",
                status="up"
            )
        )
        links.append(
            TopologyLinkSchema(
                id=f"link-site-{device.site_id}-dev-{device.id}",
                source=device.site_id,
                target=device.id,
                status="up"
            )
        )

    # 3. Add Tunnels as Links between Devices
    # To find which device a tunnel connects, we map interfaces to devices
    intf_to_dev = {
        intf.id: intf.device_id 
        for intf in db.query(Interface.id, Interface.device_id).all()
    }

    for tunnel in tunnels:
        src_dev = intf_to_dev.get(tunnel.src_interface_id)
        dst_dev = intf_to_dev.get(tunnel.dst_interface_id)
        if src_dev and dst_dev:
            links.append(
                TopologyLinkSchema(
                    id=tunnel.id,
                    source=src_dev,
                    target=dst_dev,
                    status=tunnel.status
                )
            )

    return TopologyResponseSchema(nodes=nodes, links=links)
