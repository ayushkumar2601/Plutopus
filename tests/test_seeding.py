import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../packages/shared/src")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../services/topology")))

from plutopus_shared.models import Site, Device, Interface, Tunnel, Base
from seed import seed_topology

# Setup in-memory SQLite DB
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_seeding_and_idempotency():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        # Run seeding first time
        seed_topology(db)
        
        # Check counts (Hub + 6 spoke branches)
        assert db.query(Site).count() == 7
        assert db.query(Device).count() == 7
        assert db.query(Interface).count() == 21
        assert db.query(Tunnel).count() == 12
        
        # Run seeding second time
        seed_topology(db)
        
        # Ensure no duplicates were created
        assert db.query(Site).count() == 7
        assert db.query(Device).count() == 7
        assert db.query(Interface).count() == 21
        assert db.query(Tunnel).count() == 12
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
