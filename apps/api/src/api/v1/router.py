from fastapi import APIRouter
from api.v1.endpoints import health, sites, devices, tunnels, metrics, events, topology, predictions

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(tunnels.router, prefix="/tunnels", tags=["tunnels"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(topology.router, prefix="/topology", tags=["topology"])
api_router.include_router(predictions.router, tags=["predictions"])
