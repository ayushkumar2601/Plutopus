from fastapi import APIRouter
from plutopus_schemas import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Get API status.
    """
    return HealthResponse(status="healthy")
