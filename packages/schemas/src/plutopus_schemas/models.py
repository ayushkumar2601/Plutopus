from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Status of the service")

class ApiResponse(BaseModel, Generic[T]):
    success: bool = Field(..., description="Indicates if the API request was successful")
    data: Optional[T] = Field(default=None, description="The response data payload")
    error: Optional[Any] = Field(default=None, description="Detailed error information if not successful")

class ErrorResponse(BaseModel):
    code: str = Field(..., description="Error code identifying the error type")
    message: str = Field(..., description="Human-readable error message details")
    details: Optional[Any] = Field(default=None, description="Additional structured debugging/error info")
