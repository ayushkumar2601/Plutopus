from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SiteSchema(BaseModel):
    id: str
    name: str
    role: str

    class Config:
        from_attributes = True

class DeviceSchema(BaseModel):
    id: str
    site_id: str
    name: str
    role: str
    ip: Optional[str] = None

    class Config:
        from_attributes = True

class InterfaceSchema(BaseModel):
    id: str
    device_id: str
    name: str
    type: str
    status: str

    class Config:
        from_attributes = True

class TunnelSchema(BaseModel):
    id: str
    src_interface_id: str
    dst_interface_id: str
    status: str

    class Config:
        from_attributes = True

class MetricSchema(BaseModel):
    id: int
    target_id: str
    name: str
    value: float
    timestamp: datetime

    class Config:
        from_attributes = True

class EventSchema(BaseModel):
    id: int
    device_id: str
    severity: str
    message: str
    timestamp: datetime

    class Config:
        from_attributes = True

class TopologyLinkSchema(BaseModel):
    id: str
    source: str
    target: str
    status: str

class TopologyNodeSchema(BaseModel):
    id: str
    label: str
    type: str  # hub, spoke, device
    status: str

class TopologyResponseSchema(BaseModel):
    nodes: List[TopologyNodeSchema]
    links: List[TopologyLinkSchema]
