import os
import yaml
from pathlib import Path
from sqlalchemy.orm import Session
from plutopus_shared.db import SessionLocal, Base, engine
from plutopus_shared.models import Site, Device, Interface, Tunnel

# Resolve path to topology.yaml relative to this script
TOPOLOGY_FILE = Path(__file__).parent / "topology.yaml"

def seed_topology(db: Session):
    if not TOPOLOGY_FILE.exists():
        print(f"Error: {TOPOLOGY_FILE} not found.")
        return

    with open(TOPOLOGY_FILE, "r") as f:
        data = yaml.safe_load(f)

    # 1. Seed Sites
    for site_data in data.get("sites", []):
        site_id = site_data["id"]
        site = db.query(Site).filter(Site.id == site_id).first()
        if not site:
            site = Site(id=site_id, name=site_data["name"], role=site_data["role"])
            db.add(site)
            db.flush()
            print(f"Seeded Site: {site_id}")
        else:
            site.name = site_data["name"]
            site.role = site_data["role"]
            print(f"Site {site_id} already exists, updated.")

        # 2. Seed Devices
        for device_data in site_data.get("devices", []):
            device_id = device_data["id"]
            device = db.query(Device).filter(Device.id == device_id).first()
            if not device:
                device = Device(
                    id=device_id,
                    site_id=site_id,
                    name=device_data["name"],
                    role=device_data["role"],
                    ip=device_data.get("ip")
                )
                db.add(device)
                db.flush()
                print(f"  Seeded Device: {device_id}")
            else:
                device.name = device_data["name"]
                device.role = device_data["role"]
                device.ip = device_data.get("ip")
                print(f"  Device {device_id} already exists, updated.")

            # 3. Seed Interfaces
            for intf_data in device_data.get("interfaces", []):
                intf_id = intf_data["id"]
                intf = db.query(Interface).filter(Interface.id == intf_id).first()
                if not intf:
                    intf = Interface(
                        id=intf_id,
                        device_id=device_id,
                        name=intf_data["name"],
                        type=intf_data["type"],
                        status=intf_data.get("status", "up")
                    )
                    db.add(intf)
                    db.flush()
                    print(f"    Seeded Interface: {intf_id}")
                else:
                    intf.name = intf_data["name"]
                    intf.type = intf_data["type"]
                    intf.status = intf_data.get("status", "up")
                    print(f"    Interface {intf_id} already exists, updated.")

    db.commit()

    # 4. Seed Tunnels
    for tun_data in data.get("tunnels", []):
        tun_id = tun_data["id"]
        tunnel = db.query(Tunnel).filter(Tunnel.id == tun_id).first()
        if not tunnel:
            tunnel = Tunnel(
                id=tun_id,
                src_interface_id=tun_data["src_interface_id"],
                dst_interface_id=tun_data["dst_interface_id"],
                status=tun_data.get("status", "up")
            )
            db.add(tunnel)
            db.commit()
            print(f"Seeded Tunnel: {tun_id}")
        else:
            tunnel.src_interface_id = tun_data["src_interface_id"]
            tunnel.dst_interface_id = tun_data["dst_interface_id"]
            tunnel.status = tun_data.get("status", "up")
            db.commit()
            print(f"Tunnel {tun_id} already exists, updated.")

    print("Topology seeding completed successfully.")

if __name__ == "__main__":
    # Ensure tables are created first if running script directly
    Base.metadata.create_all(bind=engine)
    db_session = SessionLocal()
    try:
        seed_topology(db_session)
    finally:
        db_session.close()
