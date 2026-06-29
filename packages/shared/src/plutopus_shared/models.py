from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from plutopus_shared.db import Base

class Site(Base):
    __tablename__ = "sites"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # hub, spoke
    business_criticality = Column(String, nullable=False, default="medium")  # low, medium, high, mission_critical

    devices = relationship("Device", back_populates="site", cascade="all, delete-orphan")


class Device(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True, index=True)
    site_id = Column(String, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # edge, core, switch
    ip = Column(String, nullable=True)
    business_criticality = Column(String, nullable=False, default="medium")  # low, medium, high, mission_critical

    site = relationship("Site", back_populates="devices")
    interfaces = relationship("Interface", back_populates="device", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="device", cascade="all, delete-orphan")


class Interface(Base):
    __tablename__ = "interfaces"

    id = Column(String, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # mpls, internet, lan
    status = Column(String, nullable=False, default="up")  # up, down

    device = relationship("Device", back_populates="interfaces")


class Tunnel(Base):
    __tablename__ = "tunnels"

    id = Column(String, primary_key=True, index=True)
    src_interface_id = Column(String, ForeignKey("interfaces.id", ondelete="CASCADE"), nullable=False)
    dst_interface_id = Column(String, ForeignKey("interfaces.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, nullable=False, default="up")  # up, down

    src_interface = relationship("Interface", foreign_keys=[src_interface_id])
    dst_interface = relationship("Interface", foreign_keys=[dst_interface_id])


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_id = Column(String, nullable=False, index=True)  # interface or tunnel ID
    name = Column(String, nullable=False, index=True)       # latency, loss, utilization
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    severity = Column(String, nullable=False, index=True)  # info, warning, critical
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    device = relationship("Device", back_populates="events")


class TelemetrySnapshot(Base):
    __tablename__ = "telemetry_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    metric_count = Column(Integer, default=0)
    event_count = Column(Integer, default=0)
    healthy = Column(Boolean, default=True)


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False)  # device, interface, tunnel
    metric = Column(String, nullable=False)
    severity = Column(String, nullable=False, index=True)  # info, warning, critical
    score = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False)  # site, tunnel
    risk_score = Column(Integer, nullable=False)  # 0-100
    risk_level = Column(String, nullable=False, index=True)  # low, moderate, elevated, high
    signals = Column(String, nullable=True)  # JSON serialized signals list
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_id = Column(String, nullable=False, index=True)
    metric = Column(String, nullable=False)
    current_val = Column(Float, nullable=False)
    forecast_15m = Column(Float, nullable=False)
    forecast_30m = Column(Float, nullable=False)
    forecast_60m = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    severity = Column(String, nullable=False, index=True)  # low, medium, high, critical
    priority = Column(Integer, nullable=False, default=50) # 0-100 priority rating
    status = Column(String, nullable=False, default="active")  # active, acknowledged, resolved
    root_cause = Column(String, nullable=True)
    confidence = Column(Float, nullable=False, default=1.0)
    affected_entities = Column(String, nullable=True)  # JSON-serialized list of entity IDs
    source_anomalies = Column(String, nullable=True)   # JSON-serialized list of anomaly IDs
    source_events = Column(String, nullable=True)      # JSON-serialized list of event IDs
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    username = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    result = Column(String, nullable=False)  # success, failure
    source_ip = Column(String, nullable=True)
