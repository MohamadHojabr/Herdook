from enum import Enum
from typing import Optional
from pydantic import Field, ValidationInfo, field_validator
from core.type.base.base_request import BaseRequest

    
class RetrivalInputModel(BaseRequest):
    assistant_id: str = Field(..., min_length=1, description="Unique identifier for the assistant")    
    query:str = Field(..., min_length=1, description="Search query string")
    k:int = Field(default=5, ge=1, le=20, description="Number of results to return (1-20)")
    distance_threshold: Optional[float] = Field(
        default=None,
        ge=0,
        le=1.0,
        description="Maximum distance threshold for results (0.0-1.0)"
    )
    @field_validator('assistant_id', 'query')
    @classmethod
    def check_empty_strings(cls, v: str, info: ValidationInfo) -> str:
        """Validate that string fields are not empty or just whitespace"""
        if not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return v.strip()

    @field_validator('k')
    @classmethod
    def validate_k(cls, v: int) -> int:
        """Additional validation for k if needed"""
        if v > 100:  # Example of additional validation
            raise ValueError("k cannot be greater than 100")
        return v
    