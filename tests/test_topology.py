import os
import yaml
from pathlib import Path

TOPOLOGY_FILE = Path(__file__).parent / "../services/topology/topology.yaml"

def test_topology_file_exists():
    assert TOPOLOGY_FILE.exists()

def test_topology_structure():
    with open(TOPOLOGY_FILE, "r") as f:
        data = yaml.safe_load(f)
    
    assert "sites" in data
    assert "tunnels" in data
    
    sites = data["sites"]
    assert len(sites) == 4  # Hub + 3 branches
    
    roles = [s["role"] for s in sites]
    assert "hub" in roles
    assert "spoke" in roles
    
    tunnels = data["tunnels"]
    assert len(tunnels) == 6
