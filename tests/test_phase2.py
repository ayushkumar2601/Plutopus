import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/topology")))

from plutopus_shared.db import Base
from plutopus_shared.models import Site, Device, Interface, Tunnel, Metric, Event
from seed import seed_topology
from graph import TopologyGraphEngine
from repository import TopologyRepository
from intelligence import TopologyIntelligenceService
from health import TopologyHealthEngine
from plutopus_shared.correlation import get_metrics_for_tunnel, get_metrics_for_device, get_metrics_for_site

DATABASE_URL = "sqlite:///test_phase2.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    if os.path.exists("test_phase2.db"):
        os.remove("test_phase2.db")
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_topology(db)
    
    # Insert some mock metrics and events for health checks
    metric_util = Metric(target_id="int-br01-mpls", name="utilization", value=80.0)
    metric_loss = Metric(target_id="tun-br01-hub-mpls", name="packet_loss", value=0.5)
    metric_lat = Metric(target_id="tun-br01-hub-mpls", name="latency", value=45.0)
    db.add_all([metric_util, metric_loss, metric_lat])
    db.commit()
    db.close()
    
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_phase2.db"):
        try:
            os.remove("test_phase2.db")
        except Exception:
            pass

def test_graph_construction():
    db = TestingSessionLocal()
    try:
        engine_instance = TopologyGraphEngine()
        engine_instance.build_from_db(db)
        assert len(engine_instance.graph.nodes) == 47
        edges = engine_instance.graph.edges(data=True)
        relations = [e[2].get("relation") for e in edges]
        assert "SITE_CONTAINS_DEVICE" in relations
        assert "DEVICE_HAS_INTERFACE" in relations
    finally:
        db.close()

def test_path_calculation():
    db = TestingSessionLocal()
    try:
        engine_instance = TopologyGraphEngine()
        engine_instance.build_from_db(db)
        path_data = engine_instance.get_shortest_path("site-branch-01", "site-branch-02")
        assert path_data["hops"] == 1
        assert "site-branch-01" in path_data["path"]
        assert "site-branch-02" in path_data["path"]
        assert len(path_data["tunnels"]) > 0
    finally:
        db.close()

def test_repository_discovery():
    db = TestingSessionLocal()
    try:
        repo = TopologyRepository(db)
        
        site = repo.get_site("site-hub")
        assert site is not None
        assert site.role == "hub"
        
        devices = repo.get_site_devices("site-branch-01")
        assert len(devices) == 1
        assert devices[0].id == "dev-br01-edge"
        
        neighbors = repo.get_neighbors("dev-br01-edge")
        assert len(neighbors) > 0
        
        tunnels = repo.get_site_tunnels("site-branch-01")
        assert len(tunnels) > 0
    finally:
        db.close()

def test_topology_intelligence():
    db = TestingSessionLocal()
    try:
        intel_service = TopologyIntelligenceService(db)
        system_intel = intel_service.get_system_intelligence()
        
        assert system_intel["hubs"] == 1
        assert system_intel["spokes"] == 6
        assert system_intel["total_tunnels"] == 12
        
        hub_analysis = [s for s in system_intel["site_analysis"] if s["site"] == "site-hub"][0]
        assert hub_analysis["role"] == "hub"
        assert hub_analysis["criticality"] == "high"
    finally:
        db.close()

def test_health_calculations_extended():
    db = TestingSessionLocal()
    try:
        health_eng = TopologyHealthEngine(db)
        
        # 1. Interface status checks
        assert health_eng.calculate_interface_status("non-existent") == "unknown"
        
        # Mark interface down
        intf = db.query(Interface).filter(Interface.id == "int-br01-lan").first()
        intf.status = "down"
        db.commit()
        assert health_eng.calculate_interface_status("int-br01-lan") == "critical"
        
        # Interface high utilization (>90)
        db.add(Metric(target_id="int-br01-inet", name="utilization", value=95.0))
        db.commit()
        assert health_eng.calculate_interface_status("int-br01-inet") == "warning"
        
        # Interface degraded utilization (75-90)
        db.add(Metric(target_id="int-br01-inet", name="utilization", value=80.0))
        db.commit()
        assert health_eng.calculate_interface_status("int-br01-inet") == "degraded"

        # 2. Tunnel status checks
        assert health_eng.calculate_tunnel_status("non-existent") == "unknown"
        
        # Tunnel down
        tun = db.query(Tunnel).filter(Tunnel.id == "tun-br01-hub-inet").first()
        tun.status = "down"
        db.commit()
        assert health_eng.calculate_tunnel_status("tun-br01-hub-inet") == "critical"
        
        # Tunnel high packet loss
        db.add(Metric(target_id="tun-br01-hub-mpls", name="packet_loss", value=6.0))
        db.commit()
        assert health_eng.calculate_tunnel_status("tun-br01-hub-mpls") == "critical"
        
        # Tunnel warning packet loss
        db.add(Metric(target_id="tun-br01-hub-mpls", name="packet_loss", value=2.0))
        db.commit()
        assert health_eng.calculate_tunnel_status("tun-br01-hub-mpls") == "warning"

        # Tunnel high latency
        db.add(Metric(target_id="tun-br01-hub-mpls", name="latency", value=160.0))
        db.commit()
        assert health_eng.calculate_tunnel_status("tun-br01-hub-mpls") == "critical"

        # Tunnel degraded latency
        db.add(Metric(target_id="tun-br01-hub-mpls", name="latency", value=95.0))
        db.commit()
        assert health_eng.calculate_tunnel_status("tun-br01-hub-mpls") == "degraded"

        # 3. Site health aggregates
        assert health_eng.calculate_site_status("site-branch-01") in ["critical", "degraded", "warning"]

        # 4. Global network status branches
        # High packet loss on a tunnel to trigger critical site
        m1 = Metric(target_id="tun-br01-hub-mpls", name="packet_loss", value=6.0)
        # High utilization on interface to trigger warning interface
        m2 = Metric(target_id="int-br02-mpls", name="utilization", value=92.0)
        db.add_all([m1, m2])
        db.commit()
        
        net_status = health_eng.calculate_network_status()
        assert net_status["status"] == "critical"
        
        # Clean up metrics
        db.delete(m1)
        db.delete(m2)
        db.commit()

        # Restore states
        intf.status = "up"
        tun.status = "up"
        db.commit()
    finally:
        db.close()

def test_metric_correlation():
    db = TestingSessionLocal()
    try:
        metrics_tun = get_metrics_for_tunnel(db, "tun-br01-hub-mpls")
        assert len(metrics_tun) > 0
        
        metrics_dev = get_metrics_for_device(db, "dev-br01-edge")
        assert len(metrics_dev) > 0
        
        metrics_site = get_metrics_for_site(db, "site-branch-01")
        assert len(metrics_site) > 0
    finally:
        db.close()

def test_health_no_tunnels():
    db = TestingSessionLocal()
    try:
        dummy_site = Site(id="site-dummy", name="Dummy Site", role="spoke")
        db.add(dummy_site)
        db.commit()
        
        health_eng = TopologyHealthEngine(db)
        assert health_eng.calculate_site_status("site-dummy") == "healthy"
        
        db.delete(dummy_site)
        db.commit()
    finally:
        db.close()
