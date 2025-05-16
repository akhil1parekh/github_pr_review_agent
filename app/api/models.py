from pydantic import Field, BaseModel


class ErrorResponse(BaseModel):
    """Response model for errors."""

    detail: str = Field(..., description="Error detail")
    status_code: int = Field(..., description="HTTP status code")
    error_code: str = Field(..., description="Error code")
